import apikeys
import psycopg2
import utils
import logging

_conn = psycopg2.connect(apikeys.db_connect_string)
log = logging.getLogger(__name__)

class Track(object):
	def __init__(self, id, filename, artist, title):
		log.info("Rendering Track(%r, %r, %r, %r)", id, filename, artist, title)
		self.id = id
		self.filename = filename
		# Add some stubby metadata (in an attribute that desperately
		# wants to be renamed to something mildly useful)
		self.obj = {
			'id': id,
			'artist': artist,
			'title': title,
		}

def get_mp3(some_specifier):
	with _conn.cursor():
		# TODO: Fetch an MP3 and return its raw data
		pass

def get_many_mp3():
	"""Get a list of many (possibly all) the tracks in the database.

	Returns a list, guaranteed to be fully realized prior to finishing
	with the database cursor, for safety.
	"""
	with _conn.cursor() as cur:
		cur.execute("select id,filename,artist,title from tracks where id <> 2 order by random()")
		return [Track(*row) for row in cur.fetchall()]

def enqueue_tracks(queue):
	"""Repeatedly enumerate tracks and enqueue them.
	
	Designed to be daemonized.
	"""
	while True:
		for track in get_many_mp3():
			queue.put(track)
