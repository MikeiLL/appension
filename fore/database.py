import apikeys
import psycopg2
import utils
import logging
import Queue
import multiprocessing
import os
import hashlib
from mutagen.mp3 import MP3
from time import sleep

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
	# Select these from the tracks table to construct a track object.
	columns = "id,filename,artist,title,length,status,submitter,submitteremail,submitted,lyrics,story,comments"
	def __init__(self, id, filename, artist, title, length, status, 
				submitter, submitteremail, submitted, lyrics, story, comments):
		log.info("Rendering Track(%r, %r, %r, %r, %r, %r, %r, %r, %r)", id, filename, artist, title, \
																	length, status, story, lyrics, comments)
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
			'story': story,
			'lyrics': lyrics,
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
			'comments': comments,
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
	query = "SELECT {cols} FROM tracks WHERE {col}=%s ORDER BY {ord}""".format(cols=Track.columns, col=("'all'" if status=='all' else 'status'), ord=order_by)
	with _conn, _conn.cursor() as cur:
		cur.execute(query, (status,))
		return [Track(*row) for row in cur.fetchall()]

_track_queue = multiprocessing.Queue()
def get_track_to_play():
	"""Get a track from the database with presumption that it will be played.

	If something has been enqueued with enqueue_track(), that will be the one
	returned; otherwise, one is picked by magic.
	"""
	with _conn, _conn.cursor() as cur:
		try:
			track=_track_queue.get(False)
			log.info("Using enqueued track %s.", track.id)
		except Queue.Empty:
			cur.execute("SELECT "+Track.columns+" FROM tracks WHERE status=1 ORDER BY played,random()")
			row=cur.fetchone()
			if not row: raise ValueError("Database is empty, cannot enqueue track")
			track=Track(*row)
			log.info("Automatically picking track %s.", track.id)
		# Record that a track has been played.
		# Currently simply increments the counter; may later keep track of how long since played, etc.
		cur.execute("UPDATE tracks SET played=played+1 WHERE id=%s", (track.id,))
		return track

def enqueue_track(id):
	with _conn, _conn.cursor() as cur:
		cur.execute("UPDATE tracks SET enqueued=enqueued+1 WHERE ID=%s RETURNING "+Track.columns, (id,))
		# Assumes the ID is actually valid (will raise TypeError if not)
		_track_queue.put(Track(*cur.fetchone()))

def get_single_track(track_id):
	"""Get details for a single track by its ID"""
	with _conn, _conn.cursor() as cur:
		cur.execute("SELECT "+Track.columns+" FROM tracks WHERE id=%s", (track_id,))
		return Track(*cur.fetchone())

def get_complete_length():
	"""Get the sum of length of all active tracks."""
	with _conn, _conn.cursor() as cur:
		cur.execute("SELECT coalesce(sum(length),0) FROM tracks WHERE status = 1")
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
		cur.execute("""INSERT INTO tracks (submitter, submitteremail, lyrics, story, comments)
			VALUES (%s, %s, %s, %s, %s) RETURNING id""",
			(info.get("submitter_name",[""])[0], info.get("email",[""])[0], info.get("lyrics",[""])[0], info.get("story",[""])[0], info.get("comments",[""])[0]))
		id = cur.fetchone()[0]
		filename = "audio/%d %s"%(id, filename)
		with open(filename, "wb") as f: f.write(mp3data)
		track = MP3(filename)
		pic=next((k for k in track if k.startswith("APIC:")), None)
		pic = pic and track[pic].data
		if pic: print("length of pic: {}".format(len(pic)))
		# Note: These need to fold absent and blank both to the given string.
		try: artist = u', '.join(track['TPE1'].text)
		except KeyError: artist = info.get("artist",[""])[0] or u'(unknown artist)'
		try: title = u', '.join(track['TIT2'].text)
		except KeyError: title = info.get("track_title",[""])[0] or u'(unknown title)'
		cur.execute("UPDATE tracks SET artist=%s, title=%s, filename=%s, artwork=%s, length=%s WHERE id=%s",
			(artist,
			title,
			track.filename[6:],
			memoryview(pic) if pic else "",
			track.info.length,
			id)
		)
		return id
		
def delete_track(input):
	"""Delete the given track ID - no confirmation"""
	with _conn, _conn.cursor() as cur:
		cur.execute("""DELETE FROM tracks WHERE id = %s""", (input,))

def update_track(id, info):
	"""Update the given track ID based on the info mapping.

	This breaks encapsulation just as create_track() does."""
	with _conn, _conn.cursor() as cur:
		# Enumerate all updateable fields. If they're not provided, they won't be updated;
		# any other fields will be ignored. This is basically set intersection on a dict.
		fields = ("artist", "status", "lyrics", "story")
		param = {k:info[k][0] for k in fields if k in info}
		cur.execute("UPDATE tracks SET "+",".join(x+"=%("+x+")s" for x in param)+" WHERE id="+str(id),param)

def create_user(username, email, password):
	"""Create a new user, return the newly-created ID"""
	username = username.lower(); email = email.lower()
	if not isinstance(password, bytes): password=password.encode("utf-8")
	with _conn, _conn.cursor() as cur:
		salt = os.urandom(16)
		hash = hashlib.sha256(salt+password).hexdigest()
		pwd = salt.encode("hex")+"-"+hash
		cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s) RETURNING id", (username, email, pwd))
		return cur.fetchone()[0]

def verify_user(user_or_email, password):
	"""Verify a user name/email and password, returns the ID if valid or None if not"""
	user_or_email = user_or_email.lower()
	if not isinstance(password, bytes): password=password.encode("utf-8")
	with _conn, _conn.cursor() as cur:
		cur.execute("SELECT id,password FROM users WHERE username=%s OR email=%s", (user_or_email, user_or_email))
		for id, pwd in cur:
			if "-" not in pwd: continue
			salt, hash = pwd.split("-", 1)
			if hashlib.sha256(salt.decode("hex")+password).hexdigest()==hash:
				# Successful match.
				return id
	# If we fall through without finding anything that matches, return None.
