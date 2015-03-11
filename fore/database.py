import apikeys
import psycopg2
import utils
import logging
import Queue
import multiprocessing
import os
import re
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
	columns = "id,filename,artist,title,length,status,submitter,submitteremail,submitted,lyrics,story,comments,xfade,itrim,otrim,sequence,keywords"
	def __init__(self, id, filename, artist, title, length, status, 
				submitter, submitteremail, submitted, lyrics, story, comments, xfade, itrim, otrim, sequence, keywords):
		log.info("Rendering Track(%r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r)", id, filename, artist, title, \
																	length, status, story, lyrics, comments, xfade, itrim, otrim)

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
			'xfade': xfade, 
			'itrim': itrim,
			'otrim': otrim,
			'comments': comments,
			'sequence': sequence,
		}
		self.full_track_details = {
			'status': status,
			'submitted': submitted,
			'submitter': submitter,
			'submitteremail': submitteremail,
			'lyrics': lyrics,
			'story': story,
			'comments': comments,
			'keywords': keywords,
		}

class Lyric(object):
	# Select these from the tracks table to construct a track object.
	columns = "id,artist,lyrics"
	
	def __init__(self, id, artist, lyrics):
		couplets = [block for block in re.split(r'(?:\r\n){2,}', lyrics) if block.count('\r\n') == 1]
		couplet_count = len(couplets)
		lyrics = self.get_couplets(lyrics)
		
		self.track_lyrics = {
			'id': id,
			'artist': artist,
			'lyrics': lyrics,
			#TODO ignore lyrics that exceed sts of two (but allow for 1/2 couplets)
			'couplet_count': couplet_count,
			'couplets': couplets
		}
		
	def get_couplets(self, lyrics):
		return lyrics.splitlines(True)
		
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
def get_track_to_render():
	"""Get a track from the database with presumption that it will be played.

	If something has been enqueued with enqueue_track(), that will be the one
	returned; otherwise, one is picked by magic.
	"""
	with _conn, _conn.cursor() as cur:
		try:
			track=_track_queue.get(False)
			log.info("Using enqueued track %s.", track.id)
		except Queue.Empty:
			cur.execute("SELECT "+Track.columns+" FROM tracks WHERE status=1 ORDER BY played,sequence,id")
			row=cur.fetchone()
			if not row: raise ValueError("Database is empty, cannot enqueue track")
			track=Track(*row)
			log.info("Automatically picking track %s.", track.id)
		# Record that a track has been played.
		# Currently simply increments the counter; may later keep track of how long since played, etc.
		cur.execute("UPDATE tracks SET played=played+1 WHERE id=%s", (track.id,))
		return track
		
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
			cur.execute("SELECT "+Track.columns+" FROM tracks WHERE status=1 ORDER BY played,id")
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
		
def get_all_lyrics():
	"""Get the lyrics from all active tracks.."""
	with _conn, _conn.cursor() as cur:
		cur.execute("SELECT id, artist, lyrics FROM tracks WHERE status = 1 AND lyrics != ''")
		return [Lyric(*row) for row in cur.fetchall()]
		
def match_lyrics(word):
    with _conn, _conn.cursor() as cur:
		cur.execute("SELECT id, artist, lyrics FROM tracks WHERE lyrics ILIKE %s", ('%'+word+'%',))
		return [Lyric(*row) for row in cur.fetchall()]
		
def match_keywords(word):
    with _conn, _conn.cursor() as cur:
		cur.execute("SELECT id, artist, lyrics FROM tracks WHERE keywords ILIKE %s", ('%'+word+'%',))
		return [Lyric(*row) for row in cur.fetchall()]
		
def random_lyrics():
    with _conn, _conn.cursor() as cur:
		cur.execute("SELECT id, artist, lyrics FROM tracks WHERE lyrics != '' ORDER BY random() limit 1")
		return [Lyric(*row) for row in cur.fetchall()]

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
		
def reset_played():
    """Reset played for all tracks to 0"""
    with _conn, _conn.cursor() as cur:
        cur.execute("UPDATE tracks SET played = 0")

def update_track(id, info):
	"""Update the given track ID based on the info mapping.

	This breaks encapsulation just as create_track() does."""
	with _conn, _conn.cursor() as cur:
		# Enumerate all updateable fields. If they're not provided, they won't be updated;
		# any other fields will be ignored. This is basically set intersection on a dict.
		fields = ("artist", "status", "lyrics", "story", "xfade", "otrim", "itrim", "keywords")
		param = {k:info[k][0] for k in fields if k in info}
		cur.execute("UPDATE tracks SET "+",".join(x+"=%("+x+")s" for x in param)+" WHERE id="+str(id),param)
		
def sequence_tracks(sequence_object):
    for id, sequence in sequence_object.iteritems():
        seq = sequence_object.get(id,'')[0]
    	with _conn, _conn.cursor() as cur:
		cur.execute("UPDATE tracks SET sequence = "+str(seq)+", played = 0 WHERE id="+str(id))
	
def get_submitter_info():
    with _conn, _conn.cursor() as cur:
        query = '''SELECT submitter, submitteremail, artist, id,
                CASE WHEN lyrics !='' THEN 1
                ELSE 0
                END as lyrics,
                CASE WHEN story !='' THEN 1
                ELSE 0
                END as story
                FROM tracks ORDER by artist'''
        cur.execute(query)
        return [row for row in cur.fetchall()]
			
def update_submitter_info(submitter_object):
    for track_grouping in zip(submitter_object['track_id'],submitter_object['name'],submitter_object['email']):
        name = track_grouping[1]
        email = track_grouping[2]
    	with _conn, _conn.cursor() as cur:
		cur.execute("UPDATE tracks SET submitter = '"+str(name)+"', submitteremail = '"+str(email)+"' WHERE id="+str(track_grouping[0]))

def create_outreach_message(message):
    with _conn, _conn.cursor() as cur:
        cur.execute("INSERT INTO outreach (message) VALUES (%s) RETURNING id, message", \
											(message,))
	return [row for row in cur.fetchone()]
											
def update_outreach_message(message, id=1):
    if retrieve_outreach_message()[0] == '':
        return create_outreach_message(message)
    query = "UPDATE outreach SET message = (message) WHERE id = 1 RETURNING id, message"
    data = (message,)
    with _conn, _conn.cursor() as cur:
        cur.execute(query, data)
	return [row for row in cur.fetchone()]
											
def retrieve_outreach_message():
    with _conn, _conn.cursor() as cur:
        cur.execute("SELECT id, message FROM outreach ORDER BY id LIMIT 1")
        try:
            return [row for row in cur.fetchone()]
        except TypeError: 
            return ['', '']
		
def get_subsequent_track(track_id):
    """Return Track Object for next track in sequence."""
    with _conn, _conn.cursor() as cur:
        cur.execute("SELECT sequence FROM tracks WHERE id = "+str(track_id))
        sequence = cur.fetchone()[0]
        query = "SELECT {cols} FROM tracks WHERE sequence > {seq} ORDER BY sequence limit 1".format(cols=Track.columns, seq=str(sequence))
        cur.execute(query)
        try:
            return Track(*cur.fetchone())
        except TypeError:
            query = "SELECT {cols} FROM tracks WHERE sequence >= {seq} ORDER BY sequence limit 1".format(cols=Track.columns, seq=str(sequence))
            cur.execute(query)
            return Track(*cur.fetchone())
            
        
def get_track_filename(track_id):
    """Return filename for a specific track, or None"""
    with _conn, _conn.cursor() as cur:
        cur.execute("SELECT filename FROM tracks WHERE id = %s", (track_id,))
        for row in cur: return row[0]

def browse_tracks(letter):
    """Return artist, id for tracks, where artist name starts with letter in expression or higher, limit 20."""
    query = "SELECT {cols} FROM tracks WHERE status = 1 AND artist >= '{letter}' ORDER BY artist LIMIT 20".format(cols=Track.columns, letter=letter)
    print(query)
    with _conn, _conn.cursor() as cur:
        cur.execute(query)
        return [Track(*row) for row in cur.fetchall()]
        
def tracks_by(artist):
    """Return artist, id for tracks, where artist name starts with letter in expression"""
    with _conn, _conn.cursor() as cur:
        cur.execute("SELECT {cols} FROM tracks WHERE status = 1 AND artist = '{artist}' ORDER BY title LIMIT 20".format(cols=Track.columns, artist=artist))
        return [Track(*row) for row in cur.fetchall()]
        
def create_user(username, email, password, hex_key):
	"""Create a new user, return the newly-created ID"""
	username = username.lower(); email = email.lower();
	if not isinstance(password, bytes): password=password.encode("utf-8")
	print password
	print email
	print hex_key
	with _conn, _conn.cursor() as cur:
		salt = os.urandom(16)
		hash = hashlib.sha256(salt+password).hexdigest()
		pwd = salt.encode("hex")+"-"+hash
		try:
			cur.execute("INSERT INTO users (username, email, password, hex_key) VALUES (%s, %s, %s, %s) RETURNING id, hex_key", \
											(username, email, pwd, hex_key))
			return cur.fetchone()
		except psycopg2.IntegrityError as e:
			return "That didn't work too well because: <br/>%s<br/> Maybe you already have an account or \
					someone else is using the name you requested."%e
					
def confirm_user(id, hex_key):
    with _conn, _conn.cursor() as cur:
        cur.execute("UPDATE users SET status = 1, hex_key = '' WHERE id = %s AND hex_key = %s RETURNING username", (id, hex_key))
        return cur.fetchone()[0]

def set_user_password(user_or_email, password):
	"""Change a user's password (administratively) - returns None on success, or error message"""
	user_or_email = user_or_email.lower()
	if not isinstance(password, bytes): password=password.encode("utf-8")
	with _conn, _conn.cursor() as cur:
		salt = os.urandom(16)
		hash = hashlib.sha256(salt+password).hexdigest()
		pwd = salt.encode("hex")+"-"+hash
		cur.execute("SELECT id FROM users WHERE username=%s OR email=%s AND status=1", (user_or_email, user_or_email))
		rows=cur.fetchall()
		if len(rows)!=1: return "This works only if the user/email provided is unique."
		cur.execute("update users set password=%s where id=%s", (pwd, rows[0][0]))

def verify_user(user_or_email, password):
	"""Verify a user name/email and password, returns the ID if valid or None if not"""
	user_or_email = user_or_email.lower()
	if not isinstance(password, bytes): password=password.encode("utf-8")
	with _conn, _conn.cursor() as cur:
		cur.execute("SELECT id,password FROM users WHERE username=%s OR email=%s AND status=1", (user_or_email, user_or_email))
		for id, pwd in cur:
			if "-" not in pwd: continue
			salt, hash = pwd.split("-", 1)
			if hashlib.sha256(salt.decode("hex")+password).hexdigest()==hash:
				# Successful match.
				return id
	# If we fall through without finding anything that matches, return None.

def get_user_info(id):
	"""Return the user name and permissions level for a given UID, or (None,0) if not logged in"""
	with _conn, _conn.cursor() as cur:
		cur.execute("SELECT username, user_level FROM users WHERE id=%s", (id,))
		row = cur.fetchone()
		return row or (None, 0)
