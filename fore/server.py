"""
Forever.fm Server
by @psobot, Nov 3 2012
"""

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
import config
from . import apikeys # ImportError? Check apikeys_sample.py for instructions.
import mailer
import oracle

import os
import sys
import json
import lame
import copy
import time
import info
import uuid
import base64
import random
import wtforms
import datetime
import threading
import traceback
import subprocess
import tornado.web
import tornado.ioloop
import tornado.template
import tornadio2.server
import multiprocessing
from tornado import escape

from daemon import Daemon
from listeners import Listeners
from wtforms_tornado import Form
from assetcompiler import compiled
from wtforms import ValidationError
from sockethandler import SocketHandler
from utils import daemonize, random_hex
from bufferedqueue import BufferedReadQueue
from monitor import MonitorHandler, MonitorSocket, monitordaemon

started_at_timestamp = time.time()
started_at = datetime.datetime.utcnow()

test = 'test' in sys.argv
SECONDS_PER_FRAME = lame.SAMPLES_PER_FRAME / 44100.0

templates = tornado.template.Loader(config.template_dir)
templates.autoescape = None
first_frame = threading.Semaphore(0)

class BaseHandler(tornado.web.RequestHandler):

	def get_current_user(self):
		username, self._user_perms = database.get_user_info(int(self.get_secure_cookie("userid") or 0))
		log.warning("WE HAVE A USERID %r and username: %r", self.get_secure_cookie("userid"), username)
		if self._user_perms: return username # If perms==0, the user has been banned, and should be treated as not-logged-in.
        


class MainHandler(BaseHandler):
	mtime = 0
	template = 'index.html'
	
	def couplet_count(self, lyrics):
		total = 0
		for count in lyrics:
			total += count.track_lyrics['couplet_count']
		return total
		
	def __gen(self):
		import database
		lyrics = database.get_all_lyrics()
		complete_length = datetime.timedelta(seconds=int(database.get_complete_length()))

		kwargs = {
			'compiled': compiled,
			'open': True, # Can have this check for server load if we ever care
			'endpoint': "/all.mp3",
			'complete_length': complete_length,
			'user_name':self.current_user or 'Glitcher',
			'couplet_count': self.couplet_count(lyrics),
			'lyrics': lyrics,
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
		

class AuditionStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')			


class InfoHandler(tornado.web.RequestHandler):
	actions = []
	started = None
	samples = 0L
	duration = 0.

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


class TimingHandler(tornado.web.RequestHandler):
	def get(self):
		self.set_header("Content-Type", "application/json")
		self.write(json.dumps({"time": time.time() * 1000}, ensure_ascii=False).encode('utf-8'))


class StreamHandler(tornado.web.RequestHandler):
	clients = []
	listeners = []

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


class SocketConnection(tornadio2.conn.SocketConnection):
	__endpoints__ = {
		"/info.websocket": SocketHandler,   #TODO: Rename
		"/monitor.websocket": MonitorSocket
	}


def MpegFile(form, field):
	from pprint import pprint
	#pprint(field.__dict__)
	filename = field.raw_data[0].filename
	#if file.size > 10*1024*1024:
		#raise ValidationError("Audio file too large ( > 10mb )")
	if not field.raw_data[0].content_type in ["audio/mpeg"]:
		raise ValidationError(" must be an audio/mpeg file.")
	ext = os.path.splitext(filename)[1]
	if not ext.lower() in [".mp3"]:
		raise ValidationError(" must be an audio/mpeg file with extension .mp3.")
		
class EasyForm(Form):
	submitter_name = wtforms.TextField('submitter_name', validators=[wtforms.validators.DataRequired()], default=u'Your Name')
	email = wtforms.TextField('email', validators=[wtforms.validators.Email(), wtforms.validators.DataRequired()])
	artist = wtforms.TextField('artist', validators=[])
	track_title = wtforms.TextField('track_title', validators=[])
	mp3_file = wtforms.FileField(u'mp3_file', validators=[MpegFile])
	story = wtforms.TextAreaField('story', validators=[])
	lyrics = wtforms.TextAreaField('lyrics', validators=[])
	comments = wtforms.TextAreaField('comments', validators=[])

class Submissionform(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		form = EasyForm()
		user_name = tornado.escape.xhtml_escape(self.current_user)
		page_title="Glitch Track Submission Form."
		og_description="The solutions for all the problems we may face are hidden within the twists and turns of the The Infinite Glitch. And it's ever-growing, ever-evolving. Getting smarter."
		meta_description="The solutions for all the problems we may face are hidden within the twists and turns of the The Infinite Glitch. And it's ever-growing, ever-evolving. Getting smarter."

		self.write(templates.load("fileuploadform.html").generate(compiled=compiled, form=form, user_name=user_name, page_title=page_title,
																meta_description=meta_description, og_url=config.server_domain,
																og_description=og_description))
		

	def post(self):
		form = EasyForm(self.request.arguments)
		form.mp3_file.raw_data = self.request.files['mp3_file']
		user_name = self.current_user or 'Glitch Hacker'
		details = 'You submitted:<br/>';
		page_title="Glitch Track Submission."
		og_description="The solutions for all the problems we may face are hidden within the twists and turns of the The Infinite Glitch. And it's ever-growing, ever-evolving. Getting smarter."
		meta_description="The solutions for all the problems we may face are hidden within the twists and turns of the The Infinite Glitch. And it's ever-growing, ever-evolving. Getting smarter."

		if form.validate():
			for f in self.request.arguments:
				details += "<hr/>" + self.get_argument(f, default=None, strip=False)
			#self.request.files['mp3_file'] is an instance of tornado.httputil.HTTPFile
			fileinfo = self.request.files['mp3_file'][0]
			details += "<hr/>" + fileinfo['filename']
			database.create_track(fileinfo['body'], fileinfo['filename'], self.request.arguments)
			info = self.request.arguments
			message = "A new file, %s had been submitted by %s at %s."%(fileinfo['filename'],info.get("submitter_name",[""])[0]
																		, info.get("email",[""])[0])
			mailer.AlertMessage(message, 'New Track Submission')
			self.write(templates.load("confirm_submission.html").generate(compiled=compiled, form=form, user_name=user_name, page_title=page_title,
																			meta_description=meta_description, og_url=config.server_domain,
																			og_description=og_description))
		else:
			self.write(templates.load("fileuploadform.html").generate(compiled=compiled, form=form, user_name=user_name, page_title=page_title,
																		meta_description=meta_description, og_url=config.server_domain,
																		og_description=og_description))
			


class Recorder(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		form = EasyForm()
		user_name = tornado.escape.xhtml_escape(self.current_user)
		page_title="Glitch Track Submission Form."
		og_description="The solutions for all the problems we may face are hidden within the twists and turns of the The Infinite Glitch. And it's ever-growing, ever-evolving. Getting smarter."
		meta_description="The solutions for all the problems we may face are hidden within the twists and turns of the The Infinite Glitch. And it's ever-growing, ever-evolving. Getting smarter."

		self.write(templates.load("recorder.html").generate(compiled=compiled, user_name=user_name, notice=''))
		

	def post(self):
		from combine_tracks import render_track
		user_name = self.current_user or 'Glitch Hacker'
		details = 'You submitted:<br/>';
		page_title="Glitch Track Submission."
		og_description="The solutions for all the problems we may face are hidden within the twists and turns of the The Infinite Glitch. And it's ever-growing, ever-evolving. Getting smarter."
		meta_description="The solutions for all the problems we may face are hidden within the twists and turns of the The Infinite Glitch. And it's ever-growing, ever-evolving. Getting smarter."

		for f in self.request.arguments:
			details += "<hr/>" + self.get_argument(f, default=None, strip=False)
		data = self.get_argument("data", "")
		if data.startswith("data:audio/mp3;base64,"):
			data = data[22:] # Trim off the expected prefix
			mp3data = base64.b64decode(data)
		else:
			# TODO: Send back some sort of error. For now, that's a 500 UnboundLocalError.
			pass
		filename = self.get_argument("fname","new.mp3")
		username = self.get_argument("username","Unknown/Hacker?")
		details += "<hr/>" + filename
		database.upload_track(mp3data, filename)
		render_track(filename, 'dgacousticlikMP3.mp3', itrim=8.3)
		#threading.Thread(target=render_track, args=(filename, 'dgacousticlikMP3.mp3'), kwargs={'itrim':8.2}).start()
		info = self.request.arguments
		message = "A new file, %s had been created by %s."%(filename, username)
		mailer.AlertMessage(message, 'New A Capella Track Created')
		self.write(templates.load("recorder.html").generate(compiled=compiled, user_name=user_name, notice="Track Uploaded"))



def admin_page(user_name, deleted=0, updated=0, notice=''):
	return templates.load("administration.html").generate(
		all_tracks=database.get_many_mp3(status="all", order_by='sequence'),
		deleted=deleted, updated=updated, compiled=compiled,
		delete_url=apikeys.delete_url, edit_url=apikeys.edit_url,
		user_name=user_name, admin_url=apikeys.admin_url, notice=notice,
	)

class DeleteTrack(BaseHandler):
	@tornado.web.authenticated
	def get(self, input):
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		input = int(input) # TODO: If intification fails, send back a tidy error message, rather than just quietly deleting nothing
		log.info("Yo we got input: %r from %s", input, user_name)
		database.delete_track(input)
		self.write(admin_page(user_name, deleted=input))

class EditTrack(BaseHandler):
	@tornado.web.authenticated
	def get(self, input):
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		self.write(templates.load("track_edit.html").generate(admin_url=apikeys.admin_url, 
		track=database.get_single_track(int(input)), compiled=compiled, user_name=user_name))
		
class SequenceHandler(BaseHandler):
	@tornado.web.authenticated
	def get(self, input):
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		self.write(admin_page(user_name))
		
	def post(self):
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		database.sequence_tracks(self.request.arguments)
		self.write(admin_page(user_name, notice='Transitions Updated.'))
		
	
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
	
class AdminRender(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		self.write(admin_page(user_name))

	def post(self):
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		track_id=int(self.request.arguments['id'][0])
		database.update_track(track_id, self.request.arguments)
		self.write(admin_page(user_name, updated=track_id))
		
class Submitters(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		submitters = database.get_track_submitter_info();
		self.write(templates.load("submitters.html").generate(admin_url=apikeys.admin_url, 
			compiled=compiled, user_name=user_name, notice="", submitters=submitters, edit_url=apikeys.edit_url,
			number=1))
		
	def post(self):
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		database.update_track_submitter_info(self.request.arguments)
		submitters = database.get_track_submitter_info();
		self.write(templates.load("submitters.html").generate(admin_url=apikeys.admin_url, 
			compiled=compiled, user_name=user_name, notice="Submitter List Updated", submitters=submitters,
			edit_url=apikeys.edit_url,number=1))
		
		
class ManageTransition(BaseHandler):
	@tornado.web.authenticated
	def get(self, input):
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		self.write(templates.load("manage_transition.html").generate(admin_url=apikeys.admin_url, 
		track=database.get_single_track(int(input)), compiled=compiled, user_name=user_name,
		next_track=database.get_subsequent_track(int(input))))
		
class AuditionTransition(BaseHandler):
	@tornado.web.authenticated
	def get(self, input):
		# This is a POST endpoint only.
		return self.redirect("/")
		
	def post(self, track_id):
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		track1_id=int(self.request.arguments['track_id'][0])
		track_xfade=int(self.request.arguments['track_xfade'][0])
		track_otrim=int(self.request.arguments['track_otrim'][0])
		next_track_itrim=int(self.request.arguments['next_track_itrim'][0])
		track2_id=int(self.request.arguments['next_track_id'][0])
		pair_o_tracks = database.get_track_filename(track1_id), database.get_track_filename(track2_id)
		import audition
		threading.Thread(target=audition.audition, args=(pair_o_tracks,track_xfade, track_otrim, next_track_itrim)).start()
		self.write(templates.load("audition.html").generate(admin_url=apikeys.admin_url, 
			track=database.get_single_track(int(track1_id)), compiled=compiled, user_name=user_name,
			next_track=database.get_single_track(int(track2_id)), track_xfade=track_xfade,
			track_otrim=track_otrim, next_track_itrim=next_track_itrim))
			
class RenderGlitch(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		self.write(templates.load("rebuild_glitch.html").generate(admin_url=apikeys.admin_url, 
			compiled=compiled, user_name=user_name))
		
	def post(self):
		from mixer import rebuild_major_glitch
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		threading.Thread(target=rebuild_major_glitch).start()
		self.write(admin_page(user_name, notice="Major Glitch rebuild has been started in the background. Will complete on its own."))
		
class ConfirmTransition(BaseHandler):
	@tornado.web.authenticated
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
		
class TrackArtwork(tornado.web.RequestHandler):
	def get(self, id):
		art = database.get_track_artwork(int(id))
		# TODO: If the track hasn't been approved yet, return 404 unless the user is an admin.
		if art is None:
			self.send_error(404)
		else:
			self.set_header("Content-Type","image/jpeg")
			self.write(str(art))
			
class Oracle(Form):
	question = wtforms.TextField('question', validators=[])
	
class OracleHandler(BaseHandler):
	def get(self):
		user_name = self.current_user or 'Glitcher'
		form = Oracle()
		popular_words = oracle.popular_words(90)
		random.shuffle(popular_words)
		og_description="The solutions for all the problems we may face are hidden within the twists and turns of the The Infinite Glitch. And it's ever-growing, ever-evolving. Getting smarter."
		page_title="Ask The Glitch Oracle"
		meta_description="The solutions for all the problems we may face are hidden within the twists and turns of the The Infinite Glitch. And it's ever-growing, ever-evolving. Getting smarter."
		og_url="http://www.infiniteglitch.net/oracle"
		self.write(templates.load("oracle.html").generate(compiled=compiled, user_name=user_name, form=form, 
															question="", answer="", popular_words=popular_words[:90],
															show_cloud="none", og_description=og_description, 
															page_title=page_title, meta_description=meta_description,
															og_url=config.server_domain))
		
	def post(self):
		form = Oracle(self.request.arguments)
		user_name = self.current_user or 'Glitcher'
		og_url="http://www.infiniteglitch.net/oracle"
		if form.validate():
			info = self.request.arguments
			question = info.get("question",[""])[0]
			answer = oracle.the_oracle_speaks(question)
			og_description="Asked the glitch oracle: "+question+" and learned that "+answer.couplet['couplet'][0]+" "+answer.couplet['couplet'][1]
			page_title="The Glitch Oracle - Psychic Answers from the Infinite Glitch"
			meta_description="Asked the glitch oracle: "+question+" and learned that "+answer.couplet['couplet'][0]+" "+answer.couplet['couplet'][1]
			popular_words = oracle.popular_words(90)
			random.shuffle(popular_words)
			self.write(templates.load("oracle.html").generate(compiled=compiled, form=form, user_name=user_name,
														question=question, answer=answer, popular_words=popular_words,
														show_cloud="block", og_description=og_description, 
														page_title=page_title, meta_description=meta_description,
														og_url=og_url))
		else:
			popular_words = oracle.popular_words(90)
			random.shuffle(popular_words)
			og_description="The solutions for all the problems we may face are hidden within the twists and turns of the The Infinite Glitch. And it's ever-growing, ever-evolving. Getting smarter."
			page_title="Ask The Glitch Oracle"
			meta_description="The solutions for all the problems we may face are hidden within the twists and turns of the The Infinite Glitch. And it's ever-growing, ever-evolving. Getting smarter."
			self.write(templates.load("oracle.html").generate(compiled=compiled, form=form, user_name=user_name,
														question="", answer="", popular_words=popular_words,
														show_cloud="block", og_description=og_description, 
														page_title=page_title, meta_description=meta_description,
														og_url=og_url))

class SandBox(BaseHandler):
	def get(self):
		user_name = self.current_user or 'Glitcher'
		og_description="The world's longest pop song."
		page_title="Sandbox Page - We Test Stuff Here"
		meta_description="A page where we test implementations for Infinite Glitch."
		og_url="http://www.infiniteglitch.net/sandbox"
		self.write(templates.load("sandbox.html").generate(compiled=compiled, user_name=user_name,
														og_description=og_description, page_title=page_title,
														meta_description=meta_description,og_url=og_url))
														
class CreditsHandler(BaseHandler):
	def get(self):
		user_name = self.current_user or 'Glitcher'
		og_description="The world's longest pop song. (Credits)"
		page_title="Credits: Infinite Glitch - the world's longest pop song, by Chris Butler."
		meta_description="The people below are partially responsible for bringing you Infinite Glitch - the world's longest pop song."
		og_url="http://www.infiniteglitch.net/credits"
		self.write(templates.load("credits.html").generate(compiled=compiled, user_name=user_name,
														og_description=og_description, page_title=page_title,
														meta_description=meta_description,og_url=og_url))

class TracksByArtist(BaseHandler):
	def get(self, artist):
		user_name = self.current_user or 'Glitcher'
		tracks_by = database.tracks_by(escape.url_unescape(artist))
		og_description= tracks_by[0].track_details['artist']+" contributions to The world's longest pop song."
		page_title=tracks_by[0].track_details['artist']+": Infinite Glitch - the world's longest pop song, by Chris Butler."
		meta_description="Browse the artists who have added to the Infinite Glitch - the world's longest pop song."
		og_url="http://www.infiniteglitch.net/view_artist/"+tornado.escape.url_escape(tracks_by[0].track_details['artist'])
		self.write(templates.load("view_artist.html").generate(compiled=compiled, user_name=user_name, 
														tracks_by=tracks_by, og_description=og_description, 
														page_title=page_title, meta_description=meta_description,
														og_url=og_url))
		
class ChunkHandler(BaseHandler):
	def get(self):
		user_name = self.current_user or 'Glitcher'
		form = Oracle()
		og_description= "You can select any individual chunk of The Infinite Glitch to listen to."
		page_title="Browse Artists: Infinite Glitch - the world's longest pop song, by Chris Butler."
		meta_description="You can select any individual chunk of The Infinite Glitch to listen to."
		og_url=og_url=config.server_domain+"/choice_chunks"
		self.write(templates.load("choice_chunks.html").generate(compiled=compiled, user_name=user_name, form=form,
																	artist_tracks="", og_description=og_description, 
																	page_title=page_title, meta_description=meta_description,
																	og_url=og_url))
		
	def post(self):
		form = Oracle(self.request.arguments)
		user_name = self.current_user or 'Glitcher'
		letter = self.request.arguments['letters'][0]
		artist_tracks = database.browse_tracks(letter)
		og_description= "You can select any individual chunk of The Infinite Glitch to listen to."
		page_title="Browse Artists: Infinite Glitch - the world's longest pop song, by Chris Butler."
		meta_description="You can select any individual chunk of The Infinite Glitch to listen to."
		og_url=og_url=config.server_domain+"/choice_chunks"
		self.write(templates.load("choice_chunks.html").generate(compiled=compiled, user_name=user_name, form=form,
																	artist_tracks=artist_tracks, og_description=og_description, 
																	page_title=page_title, meta_description=meta_description,
																	og_url=og_url))
		
class UserForm(Form):
	email = wtforms.TextField('email', validators=[wtforms.validators.DataRequired(), wtforms.validators.Email()])
	password = wtforms.PasswordField('New Password', [
		wtforms.validators.Required()])
		
class CreateUser(UserForm):
	user_name = wtforms.TextField('user_name', validators=[wtforms.validators.Length(min=4, max=25), wtforms.validators.DataRequired()], default=u'Your Name')
	password = wtforms.PasswordField('New Password', [
		wtforms.validators.Required(), wtforms.validators.Length(min=8, max=25),
		wtforms.validators.EqualTo('confirm', message='Passwords must match')
	])
	confirm = wtforms.PasswordField('Repeat Password')
	accept_tos = wtforms.BooleanField('I accept the TOS', [wtforms.validators.Required()])
	
class ConfirmAccount(tornado.web.RequestHandler):
	def get(self, id, hex_string):
		form = CreateUser()
		user_name = database.confirm_user(id, hex_string)
		og_description="Infinite Glitch - the world's longest pop song, by Chris Butler."
		meta_description="""I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""	
		signup_confirmed = "Sign-up confirmed. Login with email and password."
		self.write(templates.load("login.html").generate(compiled=compiled, form=form, user_name="new glitcher", notice=signup_confirmed,
														next="/", page_title="New User Login", og_url=config.server_domain,
														meta_description=meta_description,
														og_description=og_description))

class CreateAccount(tornado.web.RequestHandler):
	def get(self):
		form = CreateUser()
		og_description="Infinite Glitch - the world's longest pop song, by Chris Butler."
		meta_description="""I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""	
		self.write(templates.load("create_account.html").generate(compiled=compiled, form=form, user_name="new glitcher", 
																	page_title="Glitch Account Sign-Up", og_url=config.server_domain,
																	meta_description=meta_description,
																	og_description=og_description))
		
	def post(self):
		form = CreateUser(self.request.arguments)
		og_description="Infinite Glitch - the world's longest pop song, by Chris Butler."
		meta_description="""I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""	
		if form.validate():
			info = self.request.arguments
			submitter_email = info.get("email",[""])[0]
			submitter_name = info.get("user_name",[""])[0]
			hex_key = random_hex()
			details = 'Account request submitted for %s. <br/>'%(submitter_email);
			new_user = database.create_user(submitter_name, submitter_email,\
										self.get_argument('password'), hex_key)
			log.warning("New User looks like %r", new_user)
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

class OutreachForm(Form):
	message = wtforms.TextField('email', validators=[wtforms.validators.DataRequired()])
		
class Message(BaseHandler):	
	@tornado.web.authenticated

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
		self.write(templates.load("message.html").generate(admin_url=apikeys.admin_url, 
			compiled=compiled, user_name=user_name, notice="", message=message))
			
	def post(self):
		form = OutreachForm(self.request.arguments)
		info = self.request.arguments
		message = info.get("message",[""])[0]
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		database.update_outreach_message(message)
		self.write(templates.load("message.html").generate(admin_url=apikeys.admin_url, 
			compiled=compiled, user_name=user_name, notice="", message=message))
			
class Outreach(BaseHandler):	
	@tornado.web.authenticated

	def get(self):
		form = OutreachForm()
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		self.write(templates.load("outreach.html").generate(admin_url=apikeys.admin_url, 
			compiled=compiled, user_name=user_name, notice="", message=message))
			
	def post(self):
		form = OutreachForm(self.request.arguments)
		info = self.request.arguments
		message = info.get("message",[""])[0]
		self.get_current_user()
		if self._user_perms<2: return self.redirect("/")
		user_name = tornado.escape.xhtml_escape(self.current_user)
		database.update_outreach_message(message)
		self.write(templates.load("outreach.html").generate(admin_url=apikeys.admin_url, 
			compiled=compiled, user_name=user_name, notice="", message=message))
	
			
class Login(BaseHandler):
	def get(self):
		form = UserForm()
		errormessage = self.get_argument("error", "")
		username = self.get_current_user()
		
		og_description="Infinite Glitch - the world's longest pop song, by Chris Butler."
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
		form = UserForm(self.request.arguments)
		
		og_description="Infinite Glitch - the world's longest pop song, by Chris Butler."
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
			self.set_status(400)
			self.write(form.errors)
			
class Logout(BaseHandler):
    def get(self):
        self.clear_cookie("userid")
        self.redirect(self.get_argument("next", "/"))


if __name__ == "__main__":
	Daemon()

	log.info("Starting %s...", config.app_name)

	log.info("Initializing read queue to hold %2.2f seconds of audio.",
			 config.frontend_buffer)
	v2_queue = BufferedReadQueue(int(config.frontend_buffer / SECONDS_PER_FRAME))
	info_queue = multiprocessing.Queue()

	daemonize(info.generate, info_queue, first_frame, InfoHandler)
	StreamHandler.clients = Listeners(v2_queue, "All", first_frame)
	daemonize(monitordaemon,StreamHandler.clients,InfoHandler.stats,{"mp3_queue":v2_queue})

	tornado.ioloop.PeriodicCallback(InfoHandler.clean, 5 * 1000).start()

	application = tornado.web.Application(
		tornadio2.TornadioRouter(SocketConnection).apply_routes([
			# Static assets for local development
			(r"/(favicon\.ico)", tornado.web.StaticFileHandler, {"path": "static/img/"}),
			(r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "static/"}),
			(r"/audio/(.*)", tornado.web.StaticFileHandler, {"path": "audio/"}),
			(r"/transition_audio/(.*)", AuditionStaticFileHandler, {"path": "transition_audio/"}),
			(r"/instrumentals/(.*)", tornado.web.StaticFileHandler, {"path": "instrumentals/"}),
			(r"/timing\.json", TimingHandler),
			(r"/all\.json", InfoHandler),
			(r"/all\.mp3", StreamHandler),
			(r"/sequence", SequenceHandler),
			(r"/monitor", MonitorHandler),
			(r"/", MainHandler),
			(r"/submit", Submissionform),
			(r"/create_account", CreateAccount),
			(r"/login", Login),
			(r"/logout", Logout),
			(r"/confirm/([0-9]+)/([A-Fa-f0-9]+)", ConfirmAccount),
			(apikeys.admin_url, AdminRender),
			(apikeys.delete_url+"/([0-9]+)", DeleteTrack),
			(apikeys.edit_url+"/([0-9]+)", EditTrack),
			(r"/manage/([0-9]+)", ManageTransition),
			(r"/audition/([0-9]+)", AuditionTransition),
			(r"/artwork/([0-9]+).jpg", TrackArtwork),
			(r"/oracle", OracleHandler),
			(r"/choice_chunks", ChunkHandler),
			(r"/view_artist/([A-Za-z0-9\+\-\.]+)", TracksByArtist),
			(r"/rebuild_glitch", RenderGlitch),
			(r"/credits", CreditsHandler),
			(r"/submitters", Submitters),
			(r"/message", Message),
			(r"/outreach", Outreach),
			(r"/recorder", Recorder),
			(r"/sb", SandBox),
		]),
		cookie_secret=apikeys.cookie_monster,
		login_url='/login',
		admin_url=apikeys.admin_url,
	)

	frame_sender = tornado.ioloop.PeriodicCallback(
		StreamHandler.stream_frames, SECONDS_PER_FRAME * 1000
	)
	frame_sender.start()

	application.listen(config.http_port)
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
	import database
	import audition
	from mixer import Mixer
	mixer = Mixer(v2_queue.raw,info_queue)
	mixer.start()
	try:
		tornado.ioloop.IOLoop.instance().start()
	except KeyboardInterrupt:
		mixer.terminate()
		raise
