"""
InfiniteGlitch Server
by Mike iLL/mZoo and Rosuav, April 8th 2014
"""

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
from . import config
from . import apikeys # ImportError? Check apikeys_sample.py for instructions.
from . import mailer
from . import oracle
from . import lame
from . import info

import os
import sys
import json
import copy
import time
import uuid
import string
import base64
import random
import socket
import wtforms
import datetime
import requests
import tempfile
import threading
import traceback
import subprocess
import tornado.web
import tornado.log
import tornado.ioloop
import tornado.options
import tornado.template
import multiprocessing
from tornado import escape
from urllib.parse import urlparse
from collections import OrderedDict
from wtforms_tornado import Form
from wtforms import ValidationError

from .daemon import Daemon
from .oracle import Couplet
from .listeners import Listeners
from .assetcompiler import compiled
from .utils import daemonize, random_hex
from .bufferedqueue import BufferedReadQueue
from .combine_tracks import render_track

started_at_timestamp = time.time()
started_at = datetime.datetime.utcnow()

page_title="Infinite Glitch - The World's Longest Recorded Pop Song, by Chris Butler."
og_description="""I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""	
meta_description="""I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""	
og_url=config.server_domain


test = 'test' in sys.argv
SECONDS_PER_FRAME = lame.SAMPLES_PER_FRAME / 44100.0

templates = tornado.template.Loader(config.template_dir)
templates.autoescape = None
first_frame = threading.Semaphore(0)

class BaseHandler(tornado.web.RequestHandler):

	def get_current_user(self):
		username, self._user_perms = database.get_user_info(int(self.get_secure_cookie("userid") or 0))
		log.info("UserID: %r and username: %r", self.get_secure_cookie("userid"), username)
		if self._user_perms: return username # If perms==0, the user has been banned, and should be treated as not-logged-in.

class NonCachingStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')			


routes = [("/(favicon\.ico)", tornado.web.StaticFileHandler, {"path": "static/img/"})]
for dir in ["static"]:
	routes.append(("/%s/(.*)"%dir, tornado.web.StaticFileHandler, {"path": dir+"/"}))
for dir in ("audio", "audition_audio", "transition_audio"):
	routes.append(("/%s/(.*)"%dir, NonCachingStaticFileHandler, {"path": dir+"/"}))

def authenticated(func):
	"""Wrapper around tornado.web.authenticated to retain the original function for introspection

	Note that tornado.web.authenticated uses functools.wraps, but in Python 2, that doesn't save
	the original function in __wrapped__ the way it does in Python 3. So we save it manually.
	For Py3, we can drop this altogether, use tornado.web.authenticated everywhere, and just use
	__wrapped__ inside route() to access the original function for introspection of argcount."""
	newfunc = tornado.web.authenticated(func)
	newfunc.original = func
	return newfunc

def route(url):
	"""Snag a class into the routes[] collection"""
	def deco(cls):
		# Check the parameter count on get() and post() methods, if they exist.
		# The expected parameter count is the number of parenthesized slots in
		# the URL, plus one for 'self'. If the function exists and has the wrong
		# number of arguments, throw a big fat noisy error, because it's only
		# going to fail on usage.
		expected = url.count("(")+1
		for fn in ('get', 'post'):
			try:
				func = getattr(cls,fn)
				func = getattr(func, "original", func).im_func
				if func.__module__ != __name__: continue # Function was inherited from elsewhere - ignore it
				args = func.func_code.co_argcount
				if args!=expected: raise TypeError("%s.%s should take %d arguments, is taking %d" % (cls.__name__, fn, expected, args))
			except AttributeError: pass
		routes.append((url, cls))
		return cls
	return deco
	
class ShowLyrics(BaseHandler):
	def couplet_count(self, lyrics):
		total = 0
		for count in lyrics:
			total += count.track_lyrics['couplet_count']
		return total
			
	def get(self):
		lyrics = database.get_all_lyrics()
		couplet_count = self.couplet_count(lyrics)
		self.write(templates.load("lyrics.html").generate(compiled=compiled, 
								user_name=self.current_user or 'Glitcher',
								lyrics=lyrics,
								couplet_count=couplet_count))
								
@route("/artwork/([0-9]+).jpg")
class TrackArtwork(tornado.web.RequestHandler):
	def get(self, id):
		art = database.get_track_artwork(int(id))
		# TODO: If the track hasn't been approved yet, return 404 unless the user is an admin.
		if not art:
			self.redirect('../static/img/Default-artwork-200.png')
		else:
			self.set_header("Content-Type","image/jpeg")
			self.write(str(art))

@route("/")
class MainHandler(BaseHandler):
	mtime = 0
	template = 'index.html'
	
	def couplet_count(self, lyrics):
		total = 0
		for count in lyrics:
			total += count.track_lyrics['couplet_count']
		return total
		
	def __gen(self):
		from . import database
		lyrics = database.get_all_lyrics()
		complete_length = datetime.timedelta(seconds=int(database.get_complete_length()))
		from_where = self.request.headers.get('Referer')
		print(111111111)

		kwargs = {
			'compiled': compiled,
			'open': True, # Can have this check for server load if we ever care
			'endpoint': "/all.mp3",
			'complete_length': complete_length,
			'user_name':self.current_user or 'Glitcher',
			'couplet_count': self.couplet_count(lyrics),
			'lyrics': lyrics,
			'og_url':og_url,
			'og_description':og_description,
			'meta_description':meta_description
		}
		if os.path.getmtime(config.template_dir + self.template) > self.mtime:
			templates.reset()
			self.mtime = time.time()
		return templates.load(self.template).generate(**kwargs)

	def head(self):
		self.__gen()
		self.finish()

	def get(self):
		self.finish(self.__gen())

# UNMIGRATED
@route("/all\.json")
class InfoHandler(tornado.web.RequestHandler):
	actions = []
	started = None
	samples = 0
	duration = 0.0

	@classmethod
	def add(self, data):
		if not self.actions:
			self.started = time.time()
		self.samples += data['samples']
		self.duration += data['duration']
		self.clean()
		log.info("Adding track info. Currently holding info for %d tracks.",
				 len(self.actions))
		self.actions.append(data)
		SocketHandler.on_segment(data)
	

	@classmethod
	def clean(cls):
		now = time.time() - config.past_played_buffer
		while cls.actions and cls.actions[0]['time'] + cls.actions[0]['duration'] < now:
			cls.actions.pop(0)

	@classmethod
	def stats(cls):
		return {
			"started": cls.started,
			"samples": cls.samples,
			"duration": cls.duration,
		}

	def get(self):
		self.set_header("Content-Type", "application/json")
		try:
			now = self.get_argument('now', None)
			if now:
				now = time.time()
				for _action in self.actions:
					if _action['time'] < now \
					and _action['time'] + _action['duration'] > now:
						action = copy.copy(_action)
						self.write(json.dumps({'frame': action, 'now': now},
								   ensure_ascii=False).encode('utf-8'))
						return
				self.write(json.dumps([]))
			else:
				self.write(json.dumps(self.actions, ensure_ascii=False).encode('utf-8'))
		except Exception:
			log.error("Could not send info burst:\n%s", traceback.format_exc())
			log.error("Data:\n%s", self.actions)
			self.write(json.dumps([]))

@route("/timing\.json")
class TimingHandler(tornado.web.RequestHandler):
	def get(self):
		self.set_header("Content-Type", "application/json")
		self.write(json.dumps({"time": time.time() * 1000}, ensure_ascii=False).encode('utf-8'))

@route("/all\.mp3")
class StreamHandler(tornado.web.RequestHandler):
	clients = []
	listeners = [] # Not currently used??

	@classmethod
	def stream_frames(cls):
		try:
			cls.clients.broadcast()
		except Exception:
			log.error("Could not broadcast due to: \n%s", traceback.format_exc())

	def head(self):
		try:
			self.set_header("Content-Type", "audio/mpeg")
			self.finish()
		except Exception:
			log.error("Error in stream.head:\n%s", traceback.format_exc())
			tornado.web.RequestHandler.send_error(self, 500)

	@tornado.web.asynchronous
	def get(self):
		log.info("Added new listener at %s.", self.request.remote_ip)
		self.set_header("Content-Type", "audio/mpeg")
		self.clients.append(self)

	def on_finish(self):
		if self in self.clients:
			self.clients.remove(self)
			log.info("Removed client at %s", self.request.remote_ip)

# WTForms all UNMIGRATED
def MpegFile(form, field):
	"""WTForms Validator"""
	try:
		filename = field.raw_data[0].filename
		#if file.size > 10*1024*1024:
			#raise ValidationError("Audio file too large ( > 10mb )")
		if not field.raw_data[0].content_type in ["audio/mpeg"]:
			raise ValidationError(" must be an audio/mpeg file.")
		ext = os.path.splitext(filename)[1]
		if not ext.lower() in [".mp3"]:
			raise ValidationError(" must be an audio/mpeg file with extension .mp3.")
	
	except AttributeError:
		raise ValidationError(" We need a valid mp3 file to create a track submission.")
		
def ImageFile(form, field):
	"""WTForms Validator"""
	try:
		filename = field.raw_data[0].filename
		ext = os.path.splitext(filename)[1]
		if not ext.lower() in [".jpg", ".png", ".bmp", ".gif", ".jpeg"]:
			raise ValidationError(" must be an image file with extension .png, .gif, .jpg or .bmp.")
		if not len(field.raw_data[0].body) < 500000:
			raise ValidationError(" should be less than 500kb (1/2 a megabyte), please.")
	except AttributeError:
		pass
		
class EasyForm(Form):
	submitter_name = wtforms.TextField('submitter_name', validators=[wtforms.validators.DataRequired()], default=u'Your Name')
	email = wtforms.TextField('email', validators=[wtforms.validators.Email(), wtforms.validators.DataRequired()])
	
class SubmissionForm(Form):
	artist = wtforms.TextField('artist', validators=[wtforms.validators.DataRequired()])
	track_title = wtforms.TextField('track_title', validators=[])
	mp3_file = wtforms.FileField(u'mp3_file', validators=[MpegFile])
	story = wtforms.TextAreaField('story', validators=[])
	lyrics = wtforms.TextAreaField('lyrics', validators=[])
	comments = wtforms.TextAreaField('comments', validators=[])
	track_source = wtforms.HiddenField('track_source', validators=[])
	track_image = wtforms.FileField(u'track_image', validators=[ImageFile])
	url = wtforms.TextField(u'url', validators=[wtforms.validators.Optional(), wtforms.validators.url(message=u"Invalid URL. If you don't have one, please just put http://www.google.com.")])

# UNMIGRATED
@route("/submit")
class Submissionform(BaseHandler):
	@authenticated
	def get(self):
		form = SubmissionForm(track_source='user_form')
		user_name = tornado.escape.xhtml_escape(self.current_user)
		page_title="Infinite Glitch Track Submission Form."
		f = open('fortunes.txt', 'r')
		fortunes = [line for line in f if not line[0] == '%']
		saying = random.choice(fortunes)
		self.write(templates.load("submit_track.html").generate(compiled=compiled, form=form, user_name=user_name, page_title=page_title,
																meta_description=meta_description, og_url=config.server_domain,
																witty_saying=saying, og_description=og_description))

	def post(self):
		user_name = self.current_user or 'Glitch Hacker'
		details = 'You submitted:<br/>';
		page_title="Glitch Track Submission Confirmation Page."
		form = SubmissionForm(self.request.arguments)
		f = open('fortunes.txt', 'r')
		fortunes = [line for line in f if not line[0] == '%']
		saying = random.choice(fortunes)
		try:
			form.mp3_file.raw_data = self.request.files['mp3_file']
		except KeyError: 
			pass
		try:
			form.track_image.raw_data = self.request.files['track_image']
		except KeyError: 
			pass
			
		if self.request.arguments['track_source'] == ['user_form']:
			if form.validate():
					fileinfo = self.request.files['mp3_file'][0]
					try:
						track_image_file = self.request.files['track_image'][0]['body']
					except KeyError:
						track_image_file = 0
					body = fileinfo['body']
					filename = fileinfo['filename']
					for f in self.request.arguments:
						details += "<hr/>" + self.get_argument(f, default=None, strip=False)
					#self.request.files['mp3_file'] is an instance of tornado.httputil.HTTPFile
					database.create_track(body, filename, self.request.arguments, track_image_file, user_name)
					message = "A new file, %s had been submitted by %s."%(filename, user_name)
					mailer.AlertMessage(message, 'New Track Submission')
					self.write(templates.load("confirm_submission.html").generate(compiled=compiled, form=form, user_name=user_name, page_title=page_title,
													meta_description=meta_description, og_url=config.server_domain,
													og_description=og_description))
			else:
				log.info("Failed Form Submission.")
				self.write(templates.load("submit_track.html").generate(compiled=compiled, form=form, user_name=user_name, page_title=page_title,
												meta_description=meta_description, og_url=config.server_domain,
												witty_saying=saying, og_description=og_description))

		else:
			#Do this if track is already in browser memory from Glitch Studio
			#Delete MP3 field w/o validator because file is already on the server
			form.__delitem__('mp3_file')
			filename = self.request.arguments['mp3Name'][0]
			with open("audition_audio/"+filename,"rb") as f: body = f.read()
			for f in self.request.arguments:
				details += "<hr/>" + self.get_argument(f, default=None, strip=False)
			try:
				track_image_file = self.request.files['track_image'][0]['body']
			except KeyError:
				track_image_file = 0
			if self.request.arguments['url'][0][:8].lower() == 'https://':
				self.request.arguments['url'][0] = self.request.arguments['url'][0][8:]
			elif self.request.arguments['url'][0][:7 ].lower() =='http://':
				self.request.arguments['url'][0] = self.request.arguments['url'][0][7:]
			database.create_track(body, filename, self.request.arguments, track_image_file, user_name)
			message = "A new Glitch Studio Track, %s had been submitted by %s."%(filename, user_name)
			mailer.AlertMessage(message, 'New Glitch Studio Track Submission')
			self.write(templates.load("confirm_submission.html").generate(compiled=compiled, form=form, user_name=user_name, page_title=page_title,
											meta_description=meta_description, og_url=config.server_domain,
											og_description=og_description))

# UNMIGRATED
@route("/recorder")
class Recorder(BaseHandler):
	@authenticated
	def get(self):
		form = SubmissionForm()
		user_name = tornado.escape.xhtml_escape(self.current_user)
		page_title="Infinite Glitch Recording Studio"

		self.write(templates.load("recorder.html").generate(compiled=compiled, user_name=user_name, notice='', page_title=page_title,
								meta_description=meta_description, og_url=config.server_domain,
								og_description=og_description, form=form))
		

	def post(self):
		user_name = self.current_user or 'Glitch Hacker'
		details = 'You submitted:<br/>';
		page_title="Glitch Track Submission"
		form = SubmissionForm(self.request.arguments)

		data = self.get_argument("data", "")
		if data.startswith("data:audio/mp3;base64,"):
			data = data[22:] # Trim off the expected prefix
			mp3data = base64.b64decode(data)
		else:
			# TODO: Send back some sort of error. For now, that's a 500 UnboundLocalError.
			pass
		filename = self.get_argument("fname","new.mp3")
		username = self.get_argument("username","Unknown/Hacker?")

		# Ensure that the file is stereo. For some reason, manipulating mono files
		# causes problems, so let's just quickly ffmpeg this thing on arrival. Note
		# that this can cause some slight loss of quality, as we're decoding from
		# MP3 and reencoding to MP3, but this shouldn't be human-visible. It's not
		# like we're doing a 1% speed change and realigning everything - it's just
		# duplicating the one channel into two. (Or maybe folding a bunch of them
		# down to a single channel, if someone uploads a 5.1 surround sound file.)
		temp, tempfn = tempfile.mkstemp(".mp3")
		os.write(temp, mp3data)
		os.close(temp)
		from mixer import ffmpeg_command
		subprocess.check_call([ffmpeg_command,"-i",tempfn,"-y","-ac","2","acapella/"+filename])
		os.remove(tempfn)

		render_track(filename, 'dgacousticlikMP3.mp3', itrim=8.3)
		info = self.request.arguments
		message = "A new file, %s had been created by %s."%(filename, username)
		mailer.AlertMessage(message, 'New A Capella Track Created')
		self.write(templates.load("recorder.html").generate(compiled=compiled, user_name=user_name, notice="Track Uploaded", page_title=page_title,
									meta_description=meta_description, og_url=config.server_domain,
									og_description=og_description,form=form))

def admin_page(user_name, deleted=0, updated=0, notice=''):
	return templates.load("administration.html").generate(
		all_tracks=database.get_many_mp3(status="all", order_by='sequence'),
		deleted=deleted, updated=updated, compiled=compiled,
		user_name=user_name, notice=notice,
	)

@route("/delete/([0-9]+)")
class DeleteTrack(BaseHandler):
	@authenticated
	def get(self, input):
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		input = int(input) # TODO: If intification fails, send back a tidy error message, rather than just quietly deleting nothing
		database.delete_track(input)
		self.write(admin_page(user_name, deleted=input))

@route("/edit/([0-9]+)")
class EditTrack(BaseHandler):
	@authenticated
	def get(self, input):
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		track = database.get_single_track(int(input))
		if track.track_details['url'] and not track.track_details['url'] in config.server_domain[11:]:
			track_url = 'http://'+track.track_details['url']	
			try:
				resp = requests.head(track_url)
				if resp.status_code == 200:
					check_url = 'Valid'
				else:
					check_url = 'Invalid'
			except requests.exceptions.ConnectionError:
				check_url = 'Invalid'
		else:
			check_url = ''
		self.write(templates.load("track_edit.html").generate(
		track=track, compiled=compiled, user_name=user_name, check_url=check_url))
	

@route("/sequence")		
class SequenceHandler(BaseHandler):
	@authenticated
	def get(self):
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		self.write(admin_page(user_name))
		
	def post(self):
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		database.sequence_tracks(self.request.arguments)
		self.write(admin_page(user_name, notice='Transitions Updated.'))
		
class Oracle(Form):
	question = wtforms.TextField('question', validators=[])

@route("/oracle")
class OracleHandler(BaseHandler):
	def get(self):
		user_name = self.current_user or 'Glitcher'
		form = Oracle()
		question = self.get_query_arguments('question')	
		popular_words = oracle.popular_words(90)
		random.shuffle(popular_words)
		if not len(question) == 0:
			question = question[0]
			show_cloud="block"
			answer = oracle.the_oracle_speaks(question)
			if answer.couplet['artist'].name['name_list'][0] == '':
				artist = answer.couplet['artist'].name['name_list'][1]
			else:
				artist = ' name_part_two '.join(answer.couplet['artist'].name['name_list']).strip()
			og_description="Asked the glitch oracle: '"+question+"' and am told '"+answer.couplet['couplet'][0]+answer.couplet['couplet'][1]+"'"
			page_title="The Glitch Oracle - Psychic Answers from the Infinite Glitch"
			meta_description="Asked the glitch oracle: '"+question+"' and am told '"+answer.couplet['couplet'][0]+answer.couplet['couplet'][1]+"'"
			og_url="http://www.infiniteglitch.net/share_oracle/"+tornado.escape.url_escape(question)+"/"+tornado.escape.url_escape(answer.couplet['couplet'][0])+"/"+tornado.escape.url_escape(answer.couplet['couplet'][1])+"/"+tornado.escape.url_escape(artist)
			self.redirect(og_url)
		else:
			question, answer = ("","")
			show_cloud="none"
			page_title="Ask The Glitch Oracle"
			og_description="Ask The Glitch Oracle"
			meta_description="Ask The Glitch Oracle"
			og_url="http://www.infiniteglitch.net/oracle"
		self.write(templates.load("oracle.html").generate(compiled=compiled, user_name=user_name, form=form, 
								question=question, answer=answer, popular_words=popular_words[:90],
								show_cloud=show_cloud, og_description=og_description, 
								page_title=page_title, meta_description=meta_description,
								og_url=og_url))
					
@route("/share_oracle/([A-Za-z0-9\+\-\.\%]*)/([A-Za-z0-9\+\-\.\%]*)/([A-Za-z0-9\+\-\.\%]*)/([A-Za-z0-9\+\-\.\_\%]*)")
class ShareOracleHandler(BaseHandler):
	def get(self, question, answer_one, answer_two, artist):
		user_name = self.current_user or 'Glitcher'
		form = Oracle()
		question = tornado.escape.url_unescape(question)
		show_cloud="block"
		answer_string = tornado.escape.url_unescape(answer_one)+tornado.escape.url_unescape(answer_two)
		artist = tornado.escape.url_unescape(artist)
		from .database import Artist
		if 'name_part_two' in artist:
			# recreate artist name as stored in db
			artist = ', '.join(artist.split(' name_part_two '))
		artist = Artist(artist)
		print(1111111111)
		print(artist.name)
		answer = Couplet(artist, answer_string)
		artist = answer.couplet['artist'].name['display_name'].strip()
		print(answer.couplet['artist'].name['name_list'])
		print('***************')
		print(artist)
		og_description="Asked the glitch oracle: '"+question+"' and am told '"+answer.couplet['couplet'][0]+answer.couplet['couplet'][1]+"'"
		page_title="The Glitch Oracle - Psychic Answers from the Infinite Glitch"
		meta_description="Asked the glitch oracle: '"+question+"' and am told '"+answer.couplet['couplet'][0]+answer.couplet['couplet'][1]+"'"
		og_url="http://www.infiniteglitch.net/share_oracle/"+tornado.escape.url_escape(question)+"/"+tornado.escape.url_escape(answer.couplet['couplet'][0])+"/"+tornado.escape.url_escape(answer.couplet['couplet'][1])+"/"+tornado.escape.url_escape(artist)
		popular_words = oracle.popular_words(90)
		random.shuffle(popular_words)

		self.write(templates.load("share_oracle.html").generate(compiled=compiled, user_name=user_name, form=form, 
								question=question, answer=answer, popular_words=popular_words[:90],
								show_cloud=show_cloud, og_description=og_description, 
								page_title=page_title, meta_description=meta_description,
								og_url=og_url))
		
# End UNMIGRATED

@route("/credits")
class CreditsHandler(BaseHandler):
	def get(self):
		user_name = self.current_user or 'Glitcher'
		og_description="The world's longest recorded pop song. (Credits)"
		page_title="Credits: Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
		meta_description="The people below are partially responsible for bringing you Infinite Glitch - the world's longest recorded pop song."
		og_url="http://www.infiniteglitch.net/credits"
		self.write(templates.load("credits.html").generate(compiled=compiled, user_name=user_name,
								og_description=og_description, page_title=page_title,
								meta_description=meta_description,og_url=og_url))

@route("/view_artist/([A-Za-z0-9\+\-\.\%]+)")
class TracksByArtist(BaseHandler):
	def get(self, artist):
		user_name = self.current_user or 'Glitcher'
		artist = artist_for_db = escape.url_unescape(artist)
		url_artist = artist
		if artist[:8] == 'sposplit':
			artist = artist[9:]
			artist_formatting = artist.split('fposplit',1)
			artist_for_db = ', '.join([part.strip() for part in artist_formatting])
			artist = ' '.join([part.strip() for part in artist_formatting[::-1]])
		tracks_by = database.tracks_by(artist_for_db)
		og_description= artist+" contributions to The world's longest recorded pop song."
		page_title=artist+": Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
		meta_description="Browse the artists who have added to the Infinite Glitch - the world's longest recorded pop song."
		og_url="http://www.infiniteglitch.net/view_artist/"+tornado.escape.url_escape(url_artist)
		self.write(templates.load("view_artist.html").generate(compiled=compiled, user_name=user_name, 
									tracks_by=tracks_by, og_description=og_description, 
									page_title=page_title, meta_description=meta_description,
									og_url=og_url))

@route("/choice_chunks")
class ChunkHandler(BaseHandler):
	def get(self):
		user_name = self.current_user or 'Glitcher'
		form = Oracle()
		og_description= "You can select any individual chunk of The Infinite Glitch to listen to."
		page_title="Browse Artists: Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
		meta_description="You can select any individual chunk of The Infinite Glitch to listen to."
		og_url=og_url=config.server_domain+"/choice_chunks"
		recent_submitters = database.get_recent_tracks(10)
		recent_order = {}
		for submitter in recent_submitters:
			if string.lower(submitter[0][:4]) == 'the ':
				recent_order[submitter[0][4:].upper()] = ('', submitter[0])
			elif len(submitter[0].split(',')) > 1:
				# if artist contains a comma, split into Last, First
				the_submitter = submitter[0].split(',')
				the_submitter[1] = the_submitter[1].lstrip()
				recent_order[the_submitter[0].upper()] = the_submitter
			else:
				recent_order[submitter[0].upper()] = ('', submitter[0])
				
		ordered_submitters = OrderedDict(sorted(recent_order.items()))
		self.write(templates.load("choice_chunks.html").generate(compiled=compiled, user_name=user_name, form=form,
									artist_tracks="", recent_submitters=ordered_submitters, letter = '', og_description=og_description, 
									page_title=page_title, meta_description=meta_description,
									og_url=og_url))
									
	def alphabetize_ignore_the(self, list_of_names):
		'''Return alphabetized list of names, ignoring the word "The" in alphabetization.'''
		
		ordered_object = {}
		#TODO abstract me, please and stop wetting
		for item in list_of_names:
			if string.lower(item[0][:4]) == 'the ':
				ordered_object[item[0][4:].upper()] = ('', item[0])
			elif len(item[0].split(',')) > 1:
				# if item contains a comma, split into Last, First
				the_item = item[0].split(',')
				the_item[1] = the_item[1].lstrip()
				# Add a random number so duplicate names don't break this
				# seems like a bit of a hack. This whole approach is probably
				# less ideal than a really well composed database query.
				# Random names shouldn't be necessary as other two conditions
				# return unique values from the db.
				ordered_object[the_item[0].upper()+str(random.random())] = the_item
			else:
				ordered_object[item[0].upper()] = ('', item[0])
		return OrderedDict(sorted(ordered_object.items()))
		
	def post(self):
		form = Oracle(self.request.arguments)
		user_name = self.current_user or 'Glitcher'
		letter = self.request.arguments['letters'][0]
		
		artist_tracks = database.browse_tracks(letter)
		ordered_artists = self.alphabetize_ignore_the(artist_tracks)
		
		recent_submitters = database.get_recent_tracks(10)
		ordered_submitters = self.alphabetize_ignore_the(recent_submitters)
		
		og_description= "You can select any individual chunk of The Infinite Glitch to listen to."
		page_title="Browse Artists: Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
		meta_description="You can select any individual chunk of The Infinite Glitch to listen to."
		og_url=og_url=config.server_domain+"/choice_chunks"
		self.write(templates.load("choice_chunks.html").generate(compiled=compiled, user_name=user_name, form=form, 
									recent_submitters=ordered_submitters,
									artist_tracks=ordered_artists, letter=letter, og_description=og_description, 
									page_title=page_title, meta_description=meta_description,
									og_url=og_url))

def UserInDatabase(form, field):
	response = database.check_db_for_user(field.raw_data[0])
	if response == "There is already an account for that email.":
		raise ValidationError(response + " Need to reset your password? There's a link on the login page.")
		
def UserNotInDatabase(form, field):
	response = database.check_db_for_user(field.raw_data[0])
	if response == "No account found.":
		raise ValidationError(response + " Try a different email or just make a new account.")

class UserForm(Form):
	password = wtforms.PasswordField('New Password', [
		wtforms.validators.Required(), wtforms.validators.Length(min=8, max=25),
		wtforms.validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = wtforms.PasswordField('Repeat Password')
	email = wtforms.TextField('email', validators=[wtforms.validators.DataRequired(), wtforms.validators.Email()])
	accept_checkbox = wtforms.BooleanField('Confirm', [wtforms.validators.Required()])
	
class LoginForm(Form):
	password = wtforms.PasswordField('Password', [wtforms.validators.DataRequired()])
	email = wtforms.TextField('email', validators=[wtforms.validators.DataRequired(), wtforms.validators.Email()])
		
class CreateUser(UserForm):
	user_name = wtforms.TextField('user_name', validators=[wtforms.validators.Length(min=4, max=25), wtforms.validators.DataRequired()], default=u'Your Name')
	email = wtforms.TextField('email', validators=[wtforms.validators.DataRequired(), wtforms.validators.Email(), UserInDatabase])
	accept_checkbox = wtforms.BooleanField('I accept the TOS', [wtforms.validators.Required()])
	
class ResetRequestForm(UserForm):
	email = wtforms.TextField('email', validators=[wtforms.validators.DataRequired(), wtforms.validators.Email(), UserNotInDatabase])
	
class ResetPasswordForm(UserForm):
	email = wtforms.HiddenField('email', validators=[])

@route("/confirm/([0-9]+)/([A-Fa-f0-9]+)")
class ConfirmAccount(tornado.web.RequestHandler):
	def get(self, id, hex_string):
		form = CreateUser()
		user_name = database.confirm_user(id, hex_string)[0]
		if user_name == None:
			self.write("That link is no longer valid. Please try your procedure again and get a new link.")
		og_description="Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
		meta_description="""I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""	
		signup_confirmed = "Sign-up confirmed. Login with email and password."
		self.write(templates.load("login.html").generate(compiled=compiled, form=form, user_name="new glitcher", notice=signup_confirmed,
														next="/", page_title="New User Login", og_url=config.server_domain,
														meta_description=meta_description,
														og_description=og_description))

@route("/create_account")
class CreateAccount(tornado.web.RequestHandler):
	def get(self):
		form = CreateUser()
		og_description="Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
		meta_description="""I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""	
		self.write(templates.load("create_account.html").generate(compiled=compiled, form=form, user_name="new glitcher", 
									page_title="Glitch Account Sign-Up", og_url=config.server_domain,
									meta_description=meta_description,
									og_description=og_description))
		
	def post(self):
		form = CreateUser(self.request.arguments)
		og_description="Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
		meta_description="""I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""	
		if form.validate():
			info = self.request.arguments
			submitter_email = info.get("email",[""])[0]
			submitter_name = info.get("user_name",[""])[0]
			details = 'Account request submitted for %s. <br/>'%(submitter_email);
			new_user = database.create_user(submitter_name, submitter_email,\
										self.get_argument('password'))
			details += 'Please check your email to confirm.<br/>'
			admin_message = "New account created for %s at %s."%(submitter_name, submitter_email)
			mailer.AlertMessage(admin_message, 'New Account Created')
			confirmation_url = ("%s://%s/confirm/%s/%s" %
				  (self.request.protocol,
				  self.request.host, str(new_user[0]), str(new_user[1])))
			user_message = """Either you or someoe else just created an account at InfiniteGlitch.net. \n \r
To confirm for %s at %s, please visit %s"""%(submitter_name, submitter_email, confirmation_url)
			mailer.AlertMessage(user_message, 'Infinite Glitch Account', you=submitter_email)
			self.write(templates.load("account_confirmation.html").generate(compiled=compiled, user_name=submitter_name, 
											page_title="Glitch Account Sign-Up Confirmation",
											og_url=config.server_domain,
											meta_description=meta_description,
											og_description=og_description))
		else:
			self.write(templates.load("create_account.html").generate(compiled=compiled, form=form, user_name="new glitcher", 
										page_title="Glitch Account Sign-Up", og_url=config.server_domain,
										meta_description=meta_description,
										og_description=og_description))
										
@route("/reset_password")
class ResetPassword(tornado.web.RequestHandler):
	def get(self):
		form = ResetRequestForm()
		og_description="Reset Password : Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
		self.write(templates.load("reset_password.html").generate(compiled=compiled, form=form, user_name="new glitcher", notice='', 
									page_title="Reset Password Request", og_url=config.server_domain,
									meta_description=meta_description,
									og_description=og_description))
		
	def post(self):
		form = ResetRequestForm(self.request.arguments)
		form.__delitem__('password')
		form.__delitem__('confirm')
		og_description="Password Reset : Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
		meta_description="""I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""	
		if form.validate():
			info = self.request.arguments
			user_email = info.get("email",[""])[0]
			hex_key = random_hex()
			# set hex key for user and get user details
			username, id = database.hex_user_password(user_email, hex_key)
			user_name = username
			log.info("user info: %r %r", username, id)
			admin_message = "Password requested for %s at %s."%(user_name, user_email)
			mailer.AlertMessage(admin_message, 'Password Reset')
			confirmation_url = ("%s://%s/new_password/%s/%s" %
				  (self.request.protocol,
				  self.request.host, str(id), str(hex_key)))
			log.info(confirmation_url)
			notice = "Password reset link sent. Please check your email."
			user_message = """Either you or someoe else requested a password reset for InfiniteGlitch.net. \n \r
To confirm for %s at %s, please visit %s"""%(user_name, user_email, confirmation_url)
			mailer.AlertMessage(user_message, 'Infinite Glitch Password Reset Request', you=user_email)
			notice = "Password reset link sent. Please check your email."
			self.write(templates.load("reset_password.html").generate(compiled=compiled, user_name="Glitcher", notice=notice,
											page_title="Glitch Password Reset", form=form,
											og_url=config.server_domain,
											meta_description=meta_description,
											og_description=og_description))
		else:
			self.write(templates.load("reset_password.html").generate(compiled=compiled, form=form, user_name="new glitcher", notice='',
										page_title="Glitch Password Reset", og_url=config.server_domain,
										meta_description=meta_description,
										og_description=og_description))

@route("/new_password/([0-9]+)/([A-Fa-f0-9]+)")
class NewPassword(tornado.web.RequestHandler):
	def get(self, id, hex_string):
		id, username, email = database.test_reset_permissions(id, hex_string)
		form=ResetPasswordForm()
		if email == None:
			self.write("That link is no longer valid. Please try your procedure again and get a new link.")
			return
		og_description="Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
		meta_description="""I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""	
		self.write(templates.load("new_password.html").generate(compiled=compiled, form=form, user_name='Glitch Resetter', email=email, notice='',
								hex_key=hex_string, id=id, next="/", page_title="Create New Password ", og_url=config.server_domain,
								meta_description=meta_description,
								og_description=og_description))
								
	def post(self, id, hex_string):
		og_description="Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
		meta_description="""I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""	
		form=LoginForm(self.request.arguments)
		id, username, email = database.test_reset_permissions(id, hex_string)
		if form.validate():
			password = self.request.arguments['password'][0]
			database.reset_user_password(id, hex_string, password)
			self.write(templates.load("login.html").generate(compiled=compiled, form=form, user_name='Glitch Resetter', email=email, notice='Success! Login with your new password.',
								hex_key=hex_string, id=id, next="/", page_title="Create New Password ", og_url=config.server_domain,
								meta_description=meta_description,
								og_description=og_description))
		else:
			self.write(templates.load("new_password.html").generate(compiled=compiled, form=form, user_name='Glitch Resetter', email=email, notice='',
								hex_key=hex_string, id=id, next="/", page_title="Create New Password ", og_url=config.server_domain,
								meta_description=meta_description,
								og_description=og_description))


# Administrative Pages:
# From here all UNMIGRATED

@route("/gmin")
class AdminRender(BaseHandler):
	@authenticated
	def get(self):
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		self.write(admin_page(user_name))

	def post(self):
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		track_id=int(self.request.arguments['id'][0])
		try:
			artwork = self.request.files['artwork'][0]['body']
		except KeyError:
			artwork = None
		if self.request.arguments['url'][0][:8].lower() == 'https://':
			self.request.arguments['url'][0] = self.request.arguments['url'][0][8:]
		elif self.request.arguments['url'][0][:7 ].lower() =='http://':
			self.request.arguments['url'][0] = self.request.arguments['url'][0][7:]
		database.update_track(track_id, self.request.arguments, artwork)
		self.write(admin_page(user_name, updated=track_id))

@route("/submitters")
class Submitters(BaseHandler):
	@authenticated
	def get(self):
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		submitters = database.get_track_submitter_info()
		self.write(templates.load("submitters.html").generate(
			compiled=compiled, user_name=user_name, notice="", submitters=submitters,
			number=1))
		
	def post(self):
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		database.update_track_submitter_info(self.request.arguments)
		submitters = database.get_track_submitter_info()
		self.write(templates.load("submitters.html").generate(
			compiled=compiled, user_name=user_name, notice="Submitter List Updated", submitters=submitters,
			number=1))
			
@route("/manage/([0-9]+)")
class ManageTransition(BaseHandler):
	@authenticated
	def get(self, input):
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		self.write(templates.load("manage_transition.html").generate(
		track=database.get_single_track(int(input)), compiled=compiled, user_name=user_name,
		next_track=database.get_subsequent_track(int(input))))

@route("/audition/([0-9]+)")
class AuditionTransition(BaseHandler):
	@authenticated
	def get(self, input):
		# This is a POST endpoint only.
		return self.redirect("/")
		
	def post(self, track_id):
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		track1_id=int(self.request.arguments['track_id'][0])
		track_xfade=int(self.request.arguments['track_xfade'][0])
		track_otrim=float(self.request.arguments['track_otrim'][0])
		next_track_itrim=float(self.request.arguments['next_track_itrim'][0])
		track2_id=int(self.request.arguments['next_track_id'][0])
		pair_o_tracks = database.get_track_filename(track1_id), database.get_track_filename(track2_id)
		fn = os.urandom(4).encode("hex")+".mp3" # Give us a nice simple eight-character random hex file name
		import audition
		threading.Thread(target=audition.audition, args=(pair_o_tracks,track_xfade, track_otrim, next_track_itrim, fn)).start()
		f = open('fortunes.txt', 'r')
		fortunes = [line for line in f if not line[0] == '%']
		saying = random.choice(fortunes)
		self.write(templates.load("audition.html").generate(
			track=database.get_single_track(int(track1_id)), compiled=compiled, user_name=user_name,
			next_track=database.get_single_track(int(track2_id)), track_xfade=track_xfade,
			witty_saying=saying,track_otrim=track_otrim, next_track_itrim=next_track_itrim, trackfn=fn))

@route("/rebuild_glitch")
class RenderGlitch(BaseHandler):
	@authenticated
	def get(self):
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		self.write(templates.load("rebuild_glitch.html").generate(compiled=compiled, user_name=user_name))
		
	def post(self):
		from mixer import rebuild_major_glitch
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		threading.Thread(target=rebuild_major_glitch).start()
		self.write(admin_page(user_name, notice="Major Glitch rebuild has been started in the background. Will complete on its own."))

@route("/confirm_transition")
class ConfirmTransition(BaseHandler):
	@authenticated
	def post(self):
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		in_track_data = {}
		next_track_id = self.request.arguments.pop('next_track_id')[0]
		in_track_data['itrim'] = self.request.arguments.pop('itrim')
		out_track_id = self.request.arguments.pop('track_id')[0]
		database.update_track(out_track_id, self.request.arguments)
		database.update_track(next_track_id, in_track_data)
		self.write(admin_page(user_name, notice="Transition Settings Adjusted"))
				
@route("/sb")
class SandBox(BaseHandler):
	def get(self):
		user_name = self.current_user or 'Glitcher'
		og_description="The world's longest recorded pop song."
		page_title="Sandbox Page - We Test Stuff Here"
		meta_description="A page where we test implementations for Infinite Glitch."
		og_url="http://www.infiniteglitch.net/sandbox"
		self.write(templates.load("sandbox.html").generate(compiled=compiled, user_name=user_name,
								og_description=og_description, page_title=page_title,
								meta_description=meta_description,og_url=og_url))

class OutreachForm(Form):
	message = wtforms.TextField('email', validators=[wtforms.validators.DataRequired()])

@route("/message")
class Message(BaseHandler):	
	@authenticated

	def get(self):
		if database.retrieve_outreach_message()[1] == '':
			message = '''Well, I seem to have been possessed by The Devil Glitch, which has now gone from Major to Infinite.
We are now including lyrics and a story for each "chunk" and I'm writing to ask if you would take a minute to send back a copy of the 
lyrics from your segment and maybe a few words about the submission, which might include a bit about you, a bit about our connection
and/or a bit about the chunk itself.'''
		else:
			message = database.retrieve_outreach_message()[1]
		form = OutreachForm()
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		self.write(templates.load("message.html").generate(compiled=compiled, user_name=user_name, notice="", message=message))
			
	def post(self):
		form = OutreachForm(self.request.arguments)
		info = self.request.arguments
		message = info.get("message",[""])[0]
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		database.update_outreach_message(message)
		self.write(templates.load("message.html").generate(compiled=compiled, user_name=user_name, notice="", message=message))

@route("/outreach")
class Outreach(BaseHandler):	
	@authenticated

	def get(self):
		form = OutreachForm()
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		self.write(templates.load("outreach.html").generate(compiled=compiled, user_name=user_name, notice="", message=message))
			
	def post(self):
		form = OutreachForm(self.request.arguments)
		info = self.request.arguments
		message = info.get("message",[""])[0]
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		database.update_outreach_message(message)
		self.write(templates.load("outreach.html").generate(compiled=compiled, user_name=user_name, notice="", message=message))

@route("/login")
class Login(BaseHandler):
	def get(self):
		form = LoginForm()
		errormessage = self.get_argument("error", "")
		username = self.get_current_user()
		
		og_description="Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
		meta_description="""I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""	
		
		if self.get_current_user():
			self.redirect(self.get_argument('next', '/')) # Change this line
		else:
			self.write(templates.load("login.html").generate(compiled=compiled, form=form, next=self.get_argument('next', "/"),
							errormessage=errormessage, user_name=self.current_user, notice="", page_title="Glitch Login", 
							og_url=config.server_domain,
							meta_description=meta_description,
							og_description=og_description ))
		
	def post(self):
		form = LoginForm(self.request.arguments)
		
		og_description="Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
		meta_description="""I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""	
		
		if form.validate():
			user_id = database.verify_user(self.get_argument('email'),\
								self.get_argument('password'))
			if user_id:
				user_name, perms = database.get_user_info(user_id)
				if perms: 
					self.set_secure_cookie("userid", str(user_id)) # Banned users (perms==0) are treated as guests. (We're so nice.)
				self.redirect(self.get_argument("next", "/"))
			else:
				notice = "LOGIN FAILED. PLEASE TRY AGAIN."
				self.write(templates.load("login.html").generate(compiled=compiled, form=form, next=self.get_argument('next', "/"),
										notice=notice, user_name=self.current_user, page_title="Login Error", og_url=config.server_domain,
										meta_description=meta_description, og_description=og_description ))
		else:
			self.write(templates.load("login.html").generate(compiled=compiled, form=form, next=self.get_argument('next', "/"),
										notice='', user_name=self.current_user, page_title="Login Error", og_url=config.server_domain,
										meta_description=meta_description, og_description=og_description ))

@route("/logout")
class Logout(BaseHandler):
    def get(self):
        self.clear_cookie("userid")
        self.redirect(self.get_argument("next", "/"))

@route("/instrumental_track")    
#TODO Abstract me to accept other tracks
class GetInstrumental(BaseHandler):    
	def get(self):
	    print('i download file: /static/instrumentals/dgacousticlikMP3.mp3')

	    ifile  = open("static/instrumentals/dgacousticlikMP3.mp3", "rb")
	    self.set_header ('Content-Type', 'audio/mpeg')
	    self.set_header ('Content-Disposition', 'attachment; filename=devilGlitchAcousticInstrumental.mp3')
	    self.write (ifile.read())
	    self.finish()
	    
class NavModule(tornado.web.UIModule):
	def render(self):
		return self.render_string('modules/navigation.html')
	    
class FooterModule(tornado.web.UIModule): 
	def render(self):
		return self.render_string('modules/footer.html')

def common_log(request):
	"""Log a request using Apache's common log format.

	Provide an open file-like object 'access_log' in settings.
	"""
	request.settings['access_log'].write('%s - %s [%s] "%s %s %s" %d %s "%s" "%s"\n' % (
		request.request.remote_ip, "-", # Not currently showing the user name, but we could add it here if we wanted to
		time.strftime('%d/%b/%Y:%H:%M:%S %z'),
		request.request.method, request.request.path, request.request.version, # Header line eg "GET /whatever HTTP/1.0"
		request.get_status(), "-", # Hmm, can't seem to get size easily :(
		request.request.headers.get("Referer", "-"),
		request.request.headers.get("User-Agent", "-"),
	))

if __name__ == "__main__":
	# When the server's running normally, maintain a local log file in addition to
	# logging to stderr.
	f = logging.FileHandler("debug.log")
	f.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s:%(message)s'))
	logging.getLogger("").addHandler(f)

	Daemon()

	log.info("Starting %s...", config.app_name)

	log.info("Initializing read queue to hold %2.2f seconds of audio.",
			 config.frontend_buffer)
	v2_queue = BufferedReadQueue(int(config.frontend_buffer / SECONDS_PER_FRAME))
	info_queue = multiprocessing.Queue()

	daemonize(info.generate, info_queue, first_frame, InfoHandler)
	StreamHandler.clients = Listeners(v2_queue, "All", first_frame)

	tornado.ioloop.PeriodicCallback(InfoHandler.clean, 5 * 1000).start()

	application = tornado.web.Application(
		cookie_secret=apikeys.cookie_monster,
		login_url='/login',
		log_function=common_log,
		access_log=open("access.log", "a"),
		ui_modules={'Footer': FooterModule,
			'GlitchNavigationModule': NavModule,}
	)

	frame_sender = tornado.ioloop.PeriodicCallback(
		StreamHandler.stream_frames, SECONDS_PER_FRAME * 1000
	)
	frame_sender.start()

	tries = 0
	while True:
		try:
			tries += 1
			application.listen(config.http_port)
		except socket.error as e:
			if e.errno != 98: raise
			# If we get "address already in use", wait a bit and
			# then try again.
			if tries >= 10: raise # Try for a minute and a half, then give up.
			log.warning("Address already in use, retrying...")
			time.sleep(10)
		else:
			break
	try:
		if config.use_sudo_uid_gid:
			# Attempt to drop privs to the user that invoked sudo, if
			# possible. Otherwise, fall back on the specified uid/gid.
			uid = int(os.getenv("SUDO_UID") or 0)
			if uid: config.uid = uid
			gid = int(os.getenv("SUDO_GID") or 0)
			if uid: config.gid = gid
		if config.gid: os.setgid(config.gid)
		if config.uid: os.setuid(config.uid)
	except OSError:
		log.info("Attempted to set UID/GID %d/%d",config.uid,config.gid)
		raise
	log.info("Running as UID/GID %d/%d %d/%d",os.getuid(),os.getgid(),os.geteuid(),os.getegid())
	# Now we load up a few other modules - now that setuid is done.
	# These will be re-imported elsewhere when they're needed, but any lengthy
	# initialization work will be done at this point, before the mixer starts.
	# This slows startup slightly, but prevents the 1-2s delay on loading up
	# something like echonest.
	from . import database, audition
	from .mixer import Mixer
	mixer = Mixer(v2_queue.raw,info_queue)
	if hasattr(apikeys, 'prime_the_pump'): 
		# HACK: Prime the analysis pump to enable stall-free loading in
		# the mixer. Seems to help, although it does delay startup by
		# several seconds (one round-trip to the echonest server). See
		# comments in apikeys_sample.py for more detailed explanation.
		from amen.echo_nest_converter import AudioAnalysis
		AudioAnalysis(apikeys.prime_the_pump)
	mixer.start()
	try:
		tornado.ioloop.IOLoop.instance().start()
	except KeyboardInterrupt:
		mixer.terminate()
		raise
