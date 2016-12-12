from flask import Flask, render_template, g, Markup, request, redirect, url_for, Response
import amen.audio
import os
import time
import logging
import datetime
import threading
import subprocess
from . import config

app = Flask(__name__)

started_at_timestamp = time.time()
started_at = datetime.datetime.utcnow()

# To determine the "effective length" of the last beat, we
# average the last N beats prior to it. Higher numbers give
# smoother results but may have issues with a close-out rall.
LAST_BEAT_AVG = 10

page_title = "Infinite Glitch - The World's Longest Recorded Pop Song, by Chris Butler."
og_description = """I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""	
meta_description = """I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""	

# Import some stuff from the old package
import fore.assetcompiler
from fore import database
app.jinja_env.globals["compiled"] = fore.assetcompiler.compiled

def couplet_count(lyrics):
	total = 0
	for count in lyrics:
		total += count.track_lyrics['couplet_count']
	return total

@app.route("/")
def home():
	lyrics = database.get_all_lyrics()
	complete_length = datetime.timedelta(seconds=int(database.get_complete_length()))
	return render_template("index.html",
		open=True, # Can have this check for server load if we ever care
		endpoint="/all.mp3",
		complete_length=complete_length,
		# user_name=self.current_user or 'Glitcher', # TODO
		user_name='Glitcher', # or this
		couplet_count=couplet_count(lyrics),
		lyrics=lyrics,
		og_url=config.server_domain,
		og_description=og_description,
		meta_description=meta_description
	)

@app.route("/all.mp3")
def moosic():
	# TODO: Use proper non-blocking reads and writes here
	# Also TODO: Use a single ffmpeg process rather than one per client (dumb model to get us started)
	ffmpeg = subprocess.Popen(["ffmpeg", "-ac", "2", "-f", "s16le", "-i", "-", "-f", "mp3", "-"],
		stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
	def push_stdin():
		# TODO: Read individual files, convert to raw, process them
		# in any way we like, and send them down the wire. There, the
		# whole project is contained in one little TODO.
		try:
			nexttrack = database.get_track_to_play()
			t2 = amen.audio.Audio("audio/" + nexttrack.filename)
			skip = 0.0
			while True:
				track = nexttrack; t1 = t2
				nexttrack = database.get_track_to_play()
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

				t1b = t1.timings['beats']
				beat = sum(b.duration.total_seconds() for b in t1b[-1-LAST_BEAT_AVG:-1]) / LAST_BEAT_AVG
				t1_end = t1b[-1].time.total_seconds() + beat
				t1_length = t1.duration
				t2 = amen.audio.Audio("audio/" + nexttrack.filename)
				t2_start = t2.timings['beats'][0].time.total_seconds()
				# 1) Render t1 from skip up to (t1_end-t2_start)
				# 2) Fade across t2_start seconds - this will get us to the downbeat
				# 3) Fade across (t1_length-t1_end) seconds - this nicely rounds out the last track
				# 4) Go get the next track, but skip the first (t2_start+t1_length-t1_end) seconds
				skip = t2_start + t1_length - t1_end
				data = subprocess.run(["ffmpeg", "-i", "audio/"+track.filename, "-ac", "2", "-f", "s16le", "-"],
					stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
					check=True)
				logging.info("Sending %d bytes of data for %s", len(data.stdout), track.filename)
				ffmpeg.stdin.write(data.stdout)
		finally:
			ffmpeg.stdin.close()
	threading.Thread(target=push_stdin).start()
	def gen_output():
		while not ffmpeg.stdout.closed:
			yield ffmpeg.stdout.read1(4096)
	return Response(gen_output(), mimetype="audio/mpeg")

def run():
	if not os.path.isdir("glitch/static/assets"):
		os.mkdir("glitch/static/assets")
	app.run(host="0.0.0.0", port=config.http_port)
