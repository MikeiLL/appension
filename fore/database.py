import apikeys
import psycopg2
import utils
import logging
from mutagen.mp3 import MP3

_conn = psycopg2.connect(apikeys.db_connect_string)
log = logging.getLogger(__name__)

# Enable Unicode return values for all database queries
# This would be the default in Python 3, but in Python 2, we
# need to enable these two extensions.
# http://initd.org/psycopg/docs/usage.html#unicode-handling
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

class Track(object):
	def __init__(self, id, filename, artist, title, length, status, 
				submitter, submitteremail, submitted, lyrics, story):
		log.info("Rendering Track(%r, %r, %r, %r, %r, %r)", id, filename, artist, title, length, status)
		self.id = id
		self.filename = filename
		# Add some stubby metadata (in an attribute that desperately
		# wants to be renamed to something mildly useful)
		self.track_details = {
			'id': id,
			'artist': artist,
			'title': title,
			'length': length,
			'status': status,
		}
		self.full_track_details = {
			'id': id,
			'artist': artist,
			'title': title,
			'length': length,
			'status': status,
			'submitted': submitted,
			'submitter': submitter,
			'submitteremail': submitteremail,
			'lyrics': lyrics,
			'story': story,
		}

def get_mp3(some_specifier):
	with _conn, _conn.cursor():
		# TODO: Fetch an MP3 and return its raw data
		pass

def get_many_mp3(status=1, order_by='length'):
	"""Get a list of many (possibly all) the tracks in the database.

	Returns a list, guaranteed to be fully realized prior to finishing
	with the database cursor, for safety.
	"""
	query = """SELECT id,filename,artist,title,length,status,submitter,submitteremail,submitted,lyrics,story
		FROM tracks WHERE {col}=%s ORDER BY {ord}""".format(col=("'all'" if status=='all' else 'status'), ord=order_by)
	with _conn, _conn.cursor() as cur:
		cur.execute(query, (status,))
		return [Track(*row) for row in cur.fetchall()]
		
def get_single_track(track_id):
	"""Get details for a single track by its ID"""
	with _conn, _conn.cursor() as cur:
		cur.execute("""SELECT id,filename,artist,title,length,status,submitter,submitteremail,submitted,lyrics,story
		FROM tracks WHERE id=%s""", (track_id,))
		return Track(*cur.fetchone())

def enqueue_tracks(queue):
	"""Repeatedly enumerate tracks and enqueue them.
	
	Designed to be daemonized.
	"""
	while True:
		for track in get_many_mp3():
			queue.put(track)

def get_complete_length():
	"""Get the sum of length of all active tracks."""
	with _conn, _conn.cursor() as cur:
		cur.execute("SELECT sum(length) FROM tracks WHERE status = 1")
		return cur.fetchone()[0]

def get_track_artwork(id):
	"""Get the artwork for one track, or None if no track, or '' if no artwork."""
	with _conn, _conn.cursor() as cur:
		cur.execute("SELECT artwork FROM tracks WHERE id=%s", (id,))
		row = cur.fetchone()
		return row and row[0]

def create_track(mp3data, filename, info):
	"""Save a blob of MP3 data to the specified file and registers it in the database.

	Note that this function breaks encapsulation horribly. The third argument is
	assumed to be a request object dictionary, with all its quirks. The file is saved
	to disk as well as being registered with the database. TODO: Clean me up."""
	with _conn, _conn.cursor() as cur:
		# We have a chicken-and-egg problem here. We can't (AFAIK) get the ID3 data
		# until we have a file, and we want to name the file based on the track ID.
		# Resolution: Either save the file to a temporary name and then rename it,
		# or insert a dummy row and then update it. Using the latter approach.
		cur.execute("""INSERT INTO tracks (submitter, submitteremail, lyrics, story, notes)
			VALUES (%s, %s, %s, %s) RETURNING id""",
			(info.get("SubmitterName",[""])[0], info.get("Email",[""])[0], info.get("Lyrics",[""])[0], info.get("Story",[""])[0]), info.get("Comments",[""])[0])
		id = cur.fetchone()[0]
		filename = "audio/%d %s"%(id, filename)
		with open(filename, "wb") as f: f.write(mp3data)
		track = MP3(filename)
		pic=next((k for k in track if k.startswith("APIC:")), None)
		pic = pic and track[pic].data
		if pic: print("length of pic: {}".format(len(pic)))
		try: artist = u', '.join(track['TPE1'].text)
		except KeyError: artist = u'(unknown artist)'
		try: title = u', '.join(track['TIT2'].text)
		except KeyError: title = u'(unknown title)'
		cur.execute("UPDATE tracks SET artist=%s, title=%s, filename=%s, artwork=%s, length=%s, comments=%s WHERE id=%s",
			(artist,
			title,
			track.filename[6:],
			pic and memoryview(pic),
			track.info.length,
			comments,
			id)
		)
		return id
		
def delete_track(input):
	"""Delete the given track ID - no confirmation"""
	with _conn, _conn.cursor() as cur:
		cur.execute("""DELETE FROM tracks WHERE id = %s""", (input,))
