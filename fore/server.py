"""
Forever.fm Server
by @psobot, Nov 3 2012
"""

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
import config
import apikeys
import database

import os
import sys
import json
import lame
import copy
import time
import info
import uuid
import random
import wtforms
import datetime
import threading
import traceback
import tornado.web
import tornado.ioloop
import tornado.template
import tornadio2.server
import multiprocessing
import pyechonest.config

from mixer import Mixer
from daemon import Daemon
from utils import daemonize
from listeners import Listeners
from wtforms_tornado import Form
from assetcompiler import compiled
from sockethandler import SocketHandler
from bufferedqueue import BufferedReadQueue
from monitor import MonitorHandler, MonitorSocket, monitordaemon

#   API Key setup
pyechonest.config.ECHO_NEST_API_KEY = apikeys.ECHO_NEST_API_KEY

started_at_timestamp = time.time()
started_at = datetime.datetime.utcnow()

test = 'test' in sys.argv
SECONDS_PER_FRAME = lame.SAMPLES_PER_FRAME / 44100.0

templates = tornado.template.Loader(config.template_dir)
templates.autoescape = None
first_frame = threading.Semaphore(0)

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        username, perms = database.get_user_info(int(self.get_secure_cookie("userid")))
        if perms: return username # If perms==0, the user has been banned, and should be treated as not-logged-in.

class MainHandler(BaseHandler):
	mtime = 0
	template = 'index.html'

	def __gen(self):
		kwargs = {
			'compiled': compiled,
			'open': True, # Can have this check for server load if we ever care
			'endpoint': "/all.mp3",
			'complete_length': datetime.timedelta(seconds=int(database.get_complete_length())),
			'user_name':user_name
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

class EasyForm(Form):
	submitter_name = wtforms.TextField('submitter_name', validators=[wtforms.validators.DataRequired()], default=u'Your Name')
	email = wtforms.TextField('email', validators=[wtforms.validators.Email(), wtforms.validators.DataRequired()])
	artist = wtforms.TextField('artist', validators=[])
	track_title = wtforms.TextField('track_title', validators=[])
	mp3_file = wtforms.FileField(u'mp3_file', validators=[])
	story = wtforms.TextAreaField('story', validators=[])
	lyrics = wtforms.TextAreaField('lyrics', validators=[])
	comments = wtforms.TextAreaField('comments', validators=[])

class Submissionform(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		form = EasyForm()
		user_name = tornado.escape.xhtml_escape(self.current_user)
		self.write(templates.load("fileuploadform.html").generate(compiled=compiled, form=form, user_name=user_name))
		
	def post(self):
		form = EasyForm(self.request.arguments)
		details = 'You submitted:<br/>';
		if form.validate():
			for f in self.request.arguments:
				details += "<hr/>" + self.get_argument(f, default=None, strip=False)
			fileinfo = self.request.files['mp3_file'][0]
			details += "<hr/>" + fileinfo['filename']
			database.create_track(fileinfo['body'], fileinfo['filename'], self.request.arguments)
			self.write(details)
		else:
			self.set_status(400)
			self.write(form.errors)

def admin_page(user_name, deleted=0, updated=0):
	return templates.load("administration.html").generate(
		all_tracks=database.get_many_mp3(status="all", order_by='id'),
		deleted=deleted, updated=updated, compiled=compiled,
		delete_url=apikeys.delete_url, edit_url=apikeys.edit_url,
		user_name=user_name,
	)

class DeleteTrack(BaseHandler):
	@tornado.web.authenticated
	def get(self, input):
		input = int(input) # TODO: If intification fails, send back a tidy error message, rather than just quietly deleting nothing
		log.info("Yo we got input: %r", input)
		database.delete_track(input)
		self.write(admin_page(deleted=input))

class EditTrack(BaseHandler):
	@tornado.web.authenticated
	def get(self, input):
		user_name = tornado.escape.xhtml_escape(self.current_user)
		self.write(templates.load("audition.html").generate(admin_url=apikeys.admin_url, 
		track=database.get_single_track(int(input)), compiled=compiled, user_name=user_name))
		
class SMDemo(BaseHandler):
	def get(self):
		log.info("Yo we got input: %r", str(input))
		self.write(templates.load("sm.html").generate(endpoint="/all.mp3", compiled=compiled))
	
class AdminRender(BaseHandler):
	@tornado.web.authenticated
	def get(self):
		user_name = tornado.escape.xhtml_escape(self.current_user)
		self.write(admin_page(user_name))

	def post(self):
		id=int(self.request.arguments['id'][0])
		database.update_track(id, self.request.arguments)
		self.write(admin_page(updated=id))

class TrackArtwork(tornado.web.RequestHandler):
	def get(self, id):
		art = database.get_track_artwork(int(id))
		if art is None:
			self.send_error(404)
		else:
			self.set_header("Content-Type","image/jpeg")
			self.write(str(art))
			
class UserForm(Form):
	email = wtforms.TextField('email', validators=[wtforms.validators.DataRequired()])
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
	
	
class CreateAccount(tornado.web.RequestHandler):
	def get(self):
		form = CreateUser()
		self.write(templates.load("create_account.html").generate(compiled=compiled, form=form))
		
	def post(self):
		form = CreateUser(self.request.arguments)
		details = 'You submitted:<br/>';
		if form.validate():
			for f in self.request.arguments:
				details += "<hr/>" + self.get_argument(f, default=None, strip=False)
			database.create_user(self.get_argument('user_name'), self.get_argument('email'),\
								self.get_argument('password'))
			self.write(details)
		else:
			self.set_status(400)
			self.write(form.errors)
			
class Login(tornado.web.RequestHandler):
	def get(self):
		form = UserForm()
		try:
			errormessage = self.get_argument("error")
		except:
			errormessage = ""
		self.write(templates.load("login.html").generate(compiled=compiled, form=form, \
														errormessage = errormessage ))
		
	def post(self):
		form = UserForm(self.request.arguments)
		details = 'You submitted:<br/>';
		if form.validate():
			for f in self.request.arguments:
				details += "<hr/>" + self.get_argument(f, default=None, strip=False)
			user_id = database.verify_user(self.get_argument('email'),\
								self.get_argument('password'))
			if user_id:
				user_name, perms = database.get_user_info(user_id)
				if perms: self.set_secure_cookie("userid", str(user_id)) # Banned users (perms==0) are treated as guests. (We're so nice to people.)
				self.redirect(self.get_argument("next", "/"))
			else:
				self.write(details)
		else:
			self.set_status(400)
			self.write(form.errors)
			
class Logout(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect(self.get_argument("next", "/"))

class NewTabs(tornado.web.RequestHandler):
	def get(self):
		self.write(templates.load("new_tabs.html").generate(compiled=compiled,
			open=True, # Can have this check for server load if we ever care
			endpoint="/all.mp3",
			complete_length=datetime.timedelta(seconds=int(database.get_complete_length()))))

if __name__ == "__main__":
	Daemon()

	log.info("Starting %s...", config.app_name)

	log.info("Initializing read queue to hold %2.2f seconds of audio.",
			 config.frontend_buffer)
	v2_queue = BufferedReadQueue(int(config.frontend_buffer / SECONDS_PER_FRAME))
	info_queue = multiprocessing.Queue()

	mixer = Mixer(v2_queue.raw,info_queue)
	mixer.start()

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

			(r"/timing\.json", TimingHandler),

			(r"/all\.json", InfoHandler),
			(r"/all\.mp3", StreamHandler),

			(r"/monitor", MonitorHandler),
			(r"/", MainHandler),
			(r"/submit", Submissionform),
			(r"/create_account", CreateAccount),
			(r"/login", Login),
			(r"/logout", Logout),
			(apikeys.admin_url, AdminRender),
			(apikeys.delete_url+"/([0-9]+)", DeleteTrack),
			(apikeys.edit_url+"/([0-9]+)", EditTrack),
			(r"/artwork/([0-9]+).jpg", TrackArtwork),
			(r"/nt", NewTabs),
			(r"/sm", SMDemo),
		]),
		socket_io_port=config.socket_port,
		cookie_secret=apikeys.cookie_monster,
		login_url="/login",
		enabled_protocols=['websocket', 'xhr-multipart', 'xhr-polling', 'jsonp-polling']
	)

	frame_sender = tornado.ioloop.PeriodicCallback(
		StreamHandler.stream_frames, SECONDS_PER_FRAME * 1000
	)
	frame_sender.start()

	application.listen(config.http_port)
	try:
		tornadio2.server.SocketServer(application)
	except KeyboardInterrupt:
		mixer.terminate()
		raise
