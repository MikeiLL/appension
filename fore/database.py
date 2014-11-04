import apikeys
import psycopg2
import utils

_conn = psycopg2.connect(apikeys.db_connect_string)

class Track(object):
	def __init__(self, id, filename):
		self.id = id
		self.filename = filename
		# Add some stubby metadata (in an attribute that desperately
		# wants to be renamed to something mildly useful)
		self.obj = {
			'id': id,
			'artist': 'Picasso',
			'title': 'Your Majesty',
		}

def get_mp3(some_specifier):
	with _conn.cursor():
		# TODO: Fetch an MP3 and return its raw data
		pass

def get_many_mp3():
	with _conn.cursor() as cur:
		cur.execute("select id,filename from tracks order by id")
		return [Track(int(row[0]),row[1]) for row in cur.fetchall()]


# Etcetera.
