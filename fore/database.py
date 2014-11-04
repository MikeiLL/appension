import apikeys
import psycopg2
import utils

_conn = psycopg2.connect(apikeys.db_connect_string)

class Track(object):
	def __init__(self, id, filename, artist, title):
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
	with _conn.cursor() as cur:
		cur.execute("select id,filename,artist,title from tracks order by id")
		return [Track(*row) for row in cur.fetchall()]


# Etcetera.
