from aiohttp import web
import amen.audio
import pydub
import time
import asyncio
import logging
import subprocess
from . import database

# To determine the "effective length" of the last beat, we
# average the last N beats prior to it. Higher numbers give
# smoother results but may have issues with a close-out rall.
LAST_BEAT_AVG = 10

app = web.Application()

songs = []
position = 0
track_list = []

def route(url):
	def deco(f):
		app.router.add_get(url, f)
		return f
	return deco

# ------ Helper functions for ffmpeg() -------

# The rate-limiting sleep will wait until the clock catches up to this point.
# We start it "ten seconds ago" so we get a bit of buffer to start off.
rendered_until = time.time() - 10
ffmpeg = None # aio subprocess where we're compressing to MP3
async def render(seg, fn):
	logging.info("Sending %d bytes of data for %s secs of %s", len(seg.raw_data), seg.duration_seconds, fn)
	ffmpeg.stdin.write(seg.raw_data)
	await ffmpeg.stdin.drain()
	global rendered_until; rendered_until += seg.duration_seconds
	delay = rendered_until - time.time()
	if delay > 0:
		logging.debug("And sleeping for %ds until %s", delay, rendered_until)
		await asyncio.sleep(delay)

def get_track():
	"""Get a track and load everything we need."""
	# TODO: Have proper async database calls (if we can do it without
	# massively breaking encapsulation); psycopg2 has an async mode, and
	# aiopg links that in with asyncio.
	nexttrack = database.get_track_to_play()
	dub2 = pydub.AudioSegment.from_mp3("audio/" + nexttrack.filename).set_channels(2)
	# NOTE: Calling amen with a filename invokes a second load from disk,
	# duplicating work done above. However, it will come straight from the
	# disk cache, so the only real duplication is the decode-from-MP3; and
	# timing tests show that this is a measurable but not overly costly
	# addition on top of the time to do the actual analysis. KISS.
	t2 = amen.audio.Audio("audio/" + nexttrack.filename)
	return nexttrack, t2, dub2

async def push_stdin():
	try:
		nexttrack, t2, dub2 = get_track()
		skip = 0.0
		while True:
			track = nexttrack; t1 = t2; dub1 = dub2
			nexttrack, t2, dub2 = get_track()
			# Combine this into the next track.
			# 1) Analyze using amen
			#    t1 = amen.audio.Audio(track.filename)
			# 2) Locate the end of the effective last beat
			#    t1.timings['beats'][-10:-1][*].duration -> avg
			#    t1_end = t1.timings['beats'][-1].time + avg_duration
			# 3) Locate the first beat of the next track
			#    t2 = amen.audio.Audio(nexttrack.filename)
			#    t2_start = t2.timings['beats'][0].time
			# 4) Count back from the end of the last beat
			#    t1_end - t2_start
			# 5) Cross-fade from that point to t1_end to t2_start
			# Possibly do the cross-fade in two sections, as the times
			# won't be the same. They're the fade-in duration of t1 and
			# the fade-out duration of t2. Note that they depend on each
			# other, so they can't just be stored as-is (although the
			# beat positions and durations can).

			# Note on units:
			# The Timedelta that we find in timings['beats'] can provide us
			# with float total_seconds(), or with a .value in nanoseconds.
			# We later on will prefer milliseconds, though, so we rescale.
			# In this code, all variables store ms unless otherwise stated.
			t1b = t1.timings['beats']
			beat_ns = sum(b.duration.value for b in t1b[-1-LAST_BEAT_AVG : -1]) // LAST_BEAT_AVG
			t1_end = (t1b[-1].time.value + beat_ns) // 1000000
			t1_length = int(t1.duration * 1000)
			t2_start = t2.timings['beats'][1].time.value // 1000000
			# 1) Render t1 from skip up to (t1_end-t2_start) - the bulk of the track
			bulk = dub1[skip : t1_end - t2_start]
			track_list.append({
				"id": track.id,
				"start_time": rendered_until,
				"details": track.track_details,
			})
			await render(bulk, track.filename)
			# 2) Fade across t2_start ms - this will get us to the downbeat
			# 3) Fade across (t1_length-t1_end) ms - this nicely rounds out the last track
			# 4) Go get the next track, but skip the first (t2_start+t1_length-t1_end) ms
			skip = t2_start + t1_length - t1_end
			# Dumb fade mode. Doesn't actually fade, just overlays.
			fadeout1 = dub1[t1_end - t2_start : t1_end]
			fadein1 = dub2[:t2_start]
			fade1 = fadeout1.overlay(fadein1)
			fadeout2 = dub1[t1_end:]
			fadein2 = dub2[t2_start:skip]
			fade2 = fadeout2.overlay(fadein2)
			await render(fade1, "xfade 1")
			await render(fade2, "xfade 2")
	finally:
		ffmpeg.stdin.close()

# ------ Main renderer coroutine -------

async def ffmpeg():
	logging.debug("renderer started")
	global ffmpeg
	ffmpeg = await asyncio.create_subprocess_exec("ffmpeg", "-ac", "2", "-f", "s16le", "-i", "-", "-f", "mp3", "-",
		stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
	asyncio.ensure_future(push_stdin())
	totdata = 0
	logging.debug("Waiting for data from ffmpeg...")
	chunk = b""
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
	if ffmpeg.returncode is None:
		ffmpeg.terminate()

# ------ End of main renderer. Simpler stuff follows. :) -------

@route("/all.mp3")
async def moosic(req):
	logging.debug("/all.mp3 requested")
	resp = web.StreamResponse()
	resp.content_type = "audio/mpeg"
	await resp.prepare(req)
	pos = position
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
	return web.json_response({"ts": time.time(), "tracks": track_list}, headers={"Access-Control-Allow-Origin": "*"})

def run(port=8889):
	asyncio.ensure_future(ffmpeg())
	web.run_app(app, port=port)

if __name__ == '__main__':
	run()
