from aiohttp import web
import pydub
import os
import sys
import json
import time
import asyncio
import logging
import subprocess
from . import database, config, utils

# To determine the "effective length" of the last beat, we
# average the last N beats prior to it. Higher numbers give
# smoother results but may have issues with a close-out rall.
LAST_BEAT_AVG = 10

# Nonzero integer tracking backward-incompatible changes to the
# stored track analysis data. Any time this gets incremented,
# all analysis stored in the database is invalidated, and the
# full amen.audio.Audio work will be done anew for each track.
ANALYSIS_VERSION = 2

app = web.Application()

songs = []
position = 0
track_list = []
orig_time_offset = time.time() - time.perf_counter()

def route(url):
	def deco(f):
		app.router.add_get(url, f)
		return f
	return deco

# ------ Helper functions for infinitely_glitch() -------

# The rate-limiting sleep will wait until the clock catches up to this point.
# We start it "ten seconds ago" so we get a bit of buffer to start off.
rendered_until = time.perf_counter() - 10
ffmpeg = None # aio subprocess where we're compressing to MP3
async def _render_output_audio(seg, fn):
	logging.info("Sending %d bytes of data for %s secs of %s", len(seg.raw_data), seg.duration_seconds, fn)
	ffmpeg.stdin.write(seg.raw_data)
	await ffmpeg.stdin.drain()
	global rendered_until; rendered_until += seg.duration_seconds
	delay = rendered_until - time.perf_counter()
	if delay > 0:
		ofs = time.time() - time.perf_counter()
		logging.debug("And sleeping for %ds until %s [ofs %s=>%s = %+f]",
			delay, rendered_until, orig_time_offset, ofs, ofs - orig_time_offset)
		await asyncio.sleep(delay)

# dB gain to be added/removed from all tracks
GAIN = 0.0

@utils.timeme
def _get_track():
	"""Get a track and load everything we need."""
	# TODO: Have proper async database calls (if we can do it without
	# massively breaking encapsulation); psycopg2 has an async mode, and
	# aiopg links that in with asyncio.
	nexttrack = database.get_track_to_play()
	if not nexttrack.id: return nexttrack, None, None
	# TODO: Allow an admin-controlled fade at beginning and/or end of a track.
	# This would be configured with attributes on the track object, and could
	# be saved long-term, but prob not worth it. See fade_in/fade_out methods.
	dub2 = pydub.AudioSegment.from_mp3("audio/" + nexttrack.filename).set_channels(2) + GAIN

	try: a = json.loads(nexttrack.analysis)
	except json.JSONDecodeError: a = {"version": 0} # Anything we can't parse, we ignore
	if a["version"] == ANALYSIS_VERSION:
		# We have valid analysis. Use it.
		return nexttrack, a, dub2

	# We don't have valid analysis. Call on amen.audio and do all the work.
	import amen.audio
	analysis = amen.audio.Audio("audio/" + nexttrack.filename)
	# TODO: Equalize volume?

	# Note on units:
	# The Timedelta that we find in timings['beats'] can provide us
	# with float total_seconds(), or with a .value in nanoseconds.
	# We later on will prefer milliseconds, though, so we rescale.
	# The itrim and otrim values are (as of 20170214) stored in the
	# database in seconds, so they get rescaled in infinitely_glitch.

	# Store the interesting parts of the analysis into the database.
	# Note that this dictionary should be relatively raw and simple,
	# allowing future changes to infinitely_glitch() to still use the
	# same analysis data. Bumping ANALYSIS_VERSION will incur a quite
	# significant performance cost until the new analysis propagates.
	a = {"version": ANALYSIS_VERSION,
		"duration": int(analysis.duration * 1000),
		"beats": [b.time.value // 1000000 for b in analysis.timings['beats']],
		"beat_length": [b.duration.value // 1000000 for b in analysis.timings['beats']],
	}
	database.save_analysis(nexttrack.id, json.dumps(a))
	return nexttrack, a, dub2

async def infinitely_glitch():
	try:
		nexttrack, t2, dub2 = _get_track()
		skip = nexttrack.track_details["itrim"] * 1000
		while True:
			logging.debug("Rendering track id %s itrim %s otrim %s len %s %s",
				nexttrack.id, nexttrack.track_details["itrim"], nexttrack.track_details["otrim"],
				nexttrack.track_details["length"], t2["duration"])
			track = nexttrack; t1 = t2; dub1 = dub2
			nexttrack, t2, dub2 = _get_track()
			otrim = track.track_details["otrim"] * 1000
			if not nexttrack.id:
				# No more tracks. Render the last track to the very end.
				await _render_output_audio(dub1[skip : -otrim if otrim else None], track.filename)
				logging.info("Total rendered time: %s", rendered_until)
				break
			itrim = nexttrack.track_details["itrim"] * 1000
			# Combine this into the next track:
			# 1) Analyze using amen (cacheable)
			# 2) Locate the end of the effective last beat
			# 3) Locate the first beat of the next track
			# 4) Count back from the end of the last beat
			# 5) Overlay from that point to t1_end to t2_start

			# All times are in milliseconds.
			# NOTE: Average beat length is defined according to the entire file,
			# *not* taking otrim into account (nor itrim, fwiw). This may need
			# to be changed at some point.
			avg_beat_len = sum(t1["beat_length"][-1-LAST_BEAT_AVG : -1]) // LAST_BEAT_AVG
			t1_length = t1["duration"] - otrim
			# Scan backwards through the beats until we find a "suitable" one.
			# Suitability is defined as being long enough that it gets an entire
			# average beat before running into the end of the track (either the
			# actual physical end, or the trimmed end).
			for beat in reversed(t1["beats"]):
				t1_end = beat + avg_beat_len
				if t1_end <= t1_length: break
			itrim = nexttrack.track_details["itrim"] * 1000
			# Scan forwards through the beats until we find a suitable one.
			# In this case, suitability is much simpler: if it starts after
			# the itrim, it's good enough.
			for beat in t2["beats"][1:]:
				t2_start = beat - itrim
				if t2_start >= 0: break
			# t2_start does NOT include itrim
			track_list.append({
				"id": track.id,
				"start_time": rendered_until,
				"details": track.track_details, # NOTE: The length here ignores itrim/otrim and overlay.
			})
			if nexttrack.track_details["xfade"] == -1:
				# This track has requested that it not be faded over whatever it
				# follows. So we'll render the entire current track (barring any
				# otrim), and set a minimal skip (also counting only itrim).
				await _render_output_audio(dub1[skip:t1_length], track.filename)
				logging.info("Overlaying bypassed at request of next track")
				skip = itrim
				continue
			# 1) Render t1 from skip up to (t1_end-t2_start) - the bulk of the track
			bulk = dub1[skip : t1_end - t2_start]
			await _render_output_audio(bulk, track.filename)
			# 2) Merge across t2_start ms - this will get us to the downbeat
			# 3) Merge across (t1_length-t1_end) ms - this nicely rounds out the last track
			# 4) Go get the next track, but skip the first (t2_start+t1_length-t1_end) ms
			skip = itrim + t2_start + t1_length - t1_end
			# Overlay the end of one track on the beginning of the other.
			olayout1 = dub1[t1_end - t2_start : t1_end]
			olayin1 = dub2[itrim : itrim + t2_start]
			olay1 = olayout1.overlay(olayin1)
			olayout2 = dub1[t1_end : -otrim if otrim else None]
			olayin2 = dub2[itrim + t2_start : skip]
			olay2 = olayout2.overlay(olayin2)
			await _render_output_audio(olay1, "overlay 1")
			await _render_output_audio(olay2, "overlay 2")
	except KeyboardInterrupt:
		logging.info("Infinite Glitch coroutine terminating at admin request")
	except BaseException:
		logging.warn("Infinite Glitch coroutine terminating due to exception")
		raise
	finally:
		ffmpeg.stdin.close()

# ------ Main renderer coroutine -------

async def run_ffmpeg():
	logging.debug("renderer started")
	global ffmpeg
	ffmpeg = await asyncio.create_subprocess_exec("ffmpeg", "-ac", "2", "-f", "s16le", "-i", "-", "-f", "mp3", "-",
		stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
	asyncio.ensure_future(infinitely_glitch())
	totdata = 0
	logging.debug("Waiting for data from ffmpeg...")
	chunk = b""
	try:
		while ffmpeg.returncode is None:
			data = await ffmpeg.stdout.read(4096)
			if not data: break
			totdata += len(data)
			chunk += data
			# logging.debug("Received %d bytes [%d]", totdata, len(data))
			if data.startswith(b"\xFF\xFB") and len(chunk) > 1024*1024:
				global position
				songs.append(chunk)
				logging.debug("Adding another song section [%d, %d bytes]", len(songs) + position, len(chunk))
				chunk = b""
				if len(songs) > 32:
					songs.pop(0)
					position += 1
	finally:
		if ffmpeg.returncode is None:
			logging.warn("Terminating FFMPEG due to renderer exception")
			ffmpeg.terminate()
	logging.warn("Main renderer coroutine terminating")

# ------ End of main renderer. Simpler stuff follows. :) -------

@route("/all.mp3")
async def moosic(req):
	logging.debug("/all.mp3 requested")
	resp = web.StreamResponse()
	resp.content_type = "audio/mpeg"
	await resp.prepare(req)
	# Start at most four chunks behind. If there aren't yet four chunks,
	# start as far back as we logically can.
	pos = position + len(songs[:-4])
	while True:
		if pos - position >= len(songs):
			# Not enough content. This should only happen
			# on startup, so we just queue ourselves a bit.
			await asyncio.sleep(1)
			continue
		if pos < position:
			# The client is so far behind that we've dropped
			# the chunk that would have been next. There's
			# really not much we can do; disconnect.
			break
		logging.debug("songs %d, pos %d, position %d", len(songs), pos, position)
		resp.write(songs[pos - position])
		await resp.drain()
		pos += 1
	return resp

@route("/status.json")
async def info(req):
	logging.debug("/status.json requested")
	# TODO: Clean up the track list, ditching entries way in the past.
	# It doesn't need to be an ever-growing history.
	# Currently just returns the last few, regardless of exactly how
	# far they actually are in the past.
	return web.json_response({
		"ts": time.perf_counter(), "render_time": rendered_until,
		"tracks": track_list[-5:]
	}, headers={"Access-Control-Allow-Origin": "*"})

@route("/debug.json")
async def info(req):
	return web.json_response({
		"ts": time.perf_counter(), "render_time": rendered_until,
		"tracks": track_list,
	})

async def render_all(profile):
	"""Render the entire track as a one-shot"""
	global rendered_until; rendered_until = 0 # Disable the delay
	logging.debug("enqueueing all tracks")
	database.enqueue_all_tracks(10 if profile else 1)
	logging.debug("renderer started")
	global ffmpeg
	# TODO: Should the path to next_glitch (and major_glitch, below) be
	# made relative to the script dir rather than the cwd?
	ffmpeg = await asyncio.create_subprocess_exec("ffmpeg", "-y", "-ac", "2", "-f", "s16le", "-i", "-", "glitch/static/single-audio-files/next_glitch.mp3",
		stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
	if profile:
		# Neuter the output ffmpeg process down to a simple "cat >/dev/null"
		# Allows better performance analysis of the Python code, since we're
		# not waiting for a subprocess. Note that in a live environment, any
		# time spent waiting for ffmpeg is time we can spend processing HTTP
		# requests, so this isn't actually unfair.
		ffmpeg.stdin.close(); await ffmpeg.wait()
		ffmpeg = await asyncio.create_subprocess_exec("cat", stdin=subprocess.PIPE, stdout=subprocess.DEVNULL)
	asyncio.ensure_future(infinitely_glitch())
	await ffmpeg.wait()
	logging.debug("next_glitch.mp3 rendered")
	os.replace("glitch/static/single-audio-files/next_glitch.mp3", "glitch/static/single-audio-files/major_glitch.mp3")
	logging.info("Major Glitch built successfully.")

async def render_audition(id1, id2, fn, **kw):
	"""Render the transition from one track into another"""
	global rendered_until; rendered_until = 0 # Disable the delay
	logging.debug("enqueueing tracks %s and %s into %r", id1, id2, fn)
	database.enqueue_audition(id1, id2, **kw)
	logging.debug("renderer started")
	global ffmpeg
	ffmpeg = await asyncio.create_subprocess_exec("ffmpeg", "-y", "-ac", "2", "-f", "s16le", "-i", "-", "-f", "mp3", fn,
		stdin=subprocess.PIPE)
	asyncio.ensure_future(infinitely_glitch())
	await ffmpeg.wait()
	logging.debug("%r rendered", fn)

async def serve_http(loop, port):
	sock = utils.systemd_socket()
	if sock:
		srv = await loop.create_server(app.make_handler(), sock=sock)
	else:
		srv = await loop.create_server(app.make_handler(), "0.0.0.0", port)
		sock = srv.sockets[0]
	print("Renderer listening on %s:%s" % sock.getsockname(), file=sys.stderr)

# ------ Synchronous entry points ------

def major_glitch(profile):
	loop = asyncio.get_event_loop()
	loop.run_until_complete(render_all(profile))
	loop.close()

def audition(*a, **kw):
	loop = asyncio.get_event_loop()
	loop.run_until_complete(render_audition(*a, **kw))
	loop.close()

def run(port=config.renderer_port, gain=0.0):
	global GAIN; GAIN = gain
	loop = asyncio.get_event_loop()
	loop.run_until_complete(serve_http(loop, port))
	loop.run_until_complete(run_ffmpeg())
	loop.close()
