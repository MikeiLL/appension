"""Database operations for Appension

Executable using 'python -m fore.database' - use --help for usage.
"""
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
from docstringargs import cmdline

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
	columns = "id,filename,artist,title,length,status,submitter,submitteremail,submitted,lyrics,story,comments,xfade,itrim,otrim,sequence,keywords,url"
	def __init__(self, id, filename, artist, title, length, status, 
				submitter, submitteremail, submitted, lyrics, story, comments, xfade, itrim, otrim, sequence, keywords, url):
		log.info("Rendering Track(%r, %r, %r, %r, %r, %r, %r, %r, %r, %r, %r)", id, filename, artist, title, \
											length, status, story, comments, xfade, itrim, otrim)
                if len(artist.split(',')) > 1:
                        the_artist = artist.split(',')
                        artist_exact = artist
                        artist = ' '.join([the_artist[1], the_artist[0]])
                else: artist_exact = artist
		self.id = id
		self.filename = filename
		# Add some stubby metadata (in an attribute that desperately
		# wants to be renamed to something mildly useful)
		self.track_details = {
			'id': id,
			'artist': artist,
			'artist_exact': artist_exact,
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
			'url': url,
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
		
class Submitter(object):
    def __init__(self,username,email,userid,artist,track_id,filename,lyrics,story ):
        
        self.userid = userid
        self.username = username
        self.email = email
        self.submitted = {
            'artist': artist,
            'track_id': track_id,
            'filename': filename,
            'lyrics': lyrics,
            'story': story
            }
            
class Artist(object):
        def __init__(self, artist_from_db):
                if len(artist_from_db.split(',')) > 1:
                        name_list = artist_from_db.split(',')
                        display_name = ' '.join([name_list[1], name_list[0]])
                else: 
                        display_name = artist_from_db
                        name_list = ['', artist_from_db]
                self.name =  {
                        'display_name': display_name,
                        'name_list': name_list
                        }

class Lyric(object):
	# Select these from the tracks table to construct a track object.
	columns = "id,artist,lyrics"
	
	def __init__(self, id, artist, lyrics):
		couplets = [block for block in re.split(r'(?:\r\n){2,}', lyrics) if block.count('\r\n') == 1]
		couplet_count = len(couplets)
		lyrics = self.get_couplets(lyrics)
                an_artist = Artist(artist)
		
		self.track_lyrics = {
			'id': id,
			'artist': an_artist,
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

def create_track(mp3data, filename, imagefile, info, user_name):
	"""Save a blob of MP3 data to the specified file and registers it in the database.

	Note that this function breaks encapsulation horribly. The third argument is
	assumed to be a request object dictionary, with all its quirks. The file is saved
	to disk as well as being registered with the database. TODO: Clean me up."""
	log.info(info)
	with _conn, _conn.cursor() as cur:
		# We have a chicken-and-egg problem here. We can't (AFAIK) get the ID3 data
		# until we have a file, and we want to name the file based on the track ID.
		# Resolution: Either save the file to a temporary name and then rename it,
		# or insert a dummy row and then update it. Using the latter approach.
		cur.execute("""INSERT INTO tracks (userid, lyrics, story, comments, url)
			VALUES ((
			select id from users where username = %s
			), %s, %s, %s, %s) RETURNING id""",
			(user_name, info.get("lyrics",[""])[0], info.get("story",[""])[0], info.get("comments",[""])[0],
			info.get("url",[""])[0]))
		id = cur.fetchone()[0]
		filename = "audio/%d %s"%(id, filename)
		with open(filename, "wb") as f: f.write(mp3data)
		track = MP3(filename)
		if imagefile:
		        pic = imagefile
		else:
		        pic=next((k for k in track if k.startswith("APIC:")), None)
		        pic = pic and track[pic].data
                        
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

def update_track(id, info, artwork):
	"""Update the given track ID based on the info mapping.

	This breaks encapsulation just as create_track() does."""
	print('****************')
	log.info(info)
	with _conn, _conn.cursor() as cur:
		# Enumerate all updateable fields. If they're not provided, they won't be updated;
		# any other fields will be ignored. This is basically set intersection on a dict.
		fields = ("artist", "status", "lyrics", "story", "xfade", "otrim", "itrim", "keywords", "artwork", "url")
		param = {k:info[k][0] for k in fields if k in info}
		if not artwork == None:
		        param['artwork'] = memoryview(artwork)
		else:
		    del param['artwork']
		cur.execute("UPDATE tracks SET "+",".join(x+"=%("+x+")s" for x in param)+" WHERE id="+str(id),param)
		
def sequence_tracks(sequence_object):
    for id, sequence in sequence_object.iteritems():
        seq = sequence_object.get(id,'')[0]
    	with _conn, _conn.cursor() as cur:
		cur.execute("UPDATE tracks SET sequence = "+str(seq)+", played = 0 WHERE id="+str(id))
	
def get_track_submitter_info():
    with _conn, _conn.cursor() as cur:
        query = '''SELECT a.username, a.email, a.id as userid, b.artist, b.id as track_id, b.filename,
                CASE WHEN b.lyrics !='' THEN 1
                ELSE 0
                END as lyrics,
                CASE WHEN b.story !='' THEN 1
                ELSE 0
                END as story
                FROM tracks b 
                join users a
                on a.id=b.userid GROUP by a.username, a.email, a.id, b.artist, b.id'''
        cur.execute(query)
        return [Submitter(*row) for row in cur.fetchall()]
			
def update_track_submitter_info(submitter_object):
    '''We may not need track id, but it may prove useful at some point.'''
    for track_grouping in zip(submitter_object['track_id'],submitter_object['user_id'],submitter_object['username'],submitter_object['email']):
        userid = track_grouping[1]
        name = track_grouping[2]
        email = track_grouping[3]
        track_id = track_grouping[0]
        with _conn, _conn.cursor() as cur:
            cur.execute("UPDATE users SET username = '"+str(name)+"', email = '"+str(email)+"' WHERE id = "+str(userid))
            
def add_dummy_users():
    start_default_email_number = 0
    with _conn, _conn.cursor() as cur:
        cur.execute("SELECT artist FROM tracks WHERE userid = 0 GROUP BY artist;")
        artists = cur.fetchall()
        for artist in artists:
            start_default_email_number += 1
            start_default_email = str(start_default_email_number) + '@infiniteglitch.net'
            cur.execute("INSERT INTO users (username, email) VALUES (%s, %s) RETURNING id", (artist[0], start_default_email))
            userid = cur.fetchone()
            print(artist[0], userid)
            cur.execute("UPDATE tracks SET userid = %s WHERE artist LIKE %s", (userid, artist[0]))
        
        

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
    query = "SELECT DISTINCT artist FROM tracks WHERE status = 1 AND (case when artist ilike 'The %' then substr(upper(artist), 5, 100) else upper(artist) end) >= '{letter}' ORDER BY artist LIMIT 20".format(cols=Track.columns, letter=letter)
    with _conn, _conn.cursor() as cur:
        cur.execute(query)
        return [row for row in cur.fetchall()]
        
def get_recent_tracks(number):
        """Retrieve [number] number of most recently activated tracks"""
        query = "SELECT DISTINCT artist, submitted FROM tracks WHERE status = 1 ORDER BY submitted DESC LIMIT {number}".format(cols=Track.columns, number=number)
        with _conn, _conn.cursor() as cur:
                cur.execute(query)
                return [row for row in cur.fetchall()]
        
def tracks_by(artist):
    """Return artist, id for tracks, where artist name starts with letter in expression"""
    with _conn, _conn.cursor() as cur:
        cur.execute("SELECT {cols} FROM tracks WHERE status = 1 AND trim(artist) = '{artist}' ORDER BY title LIMIT 20".format(cols=Track.columns, artist=artist))
        return [Track(*row) for row in cur.fetchall()]

@cmdline
def create_user(username, email, password, hex_key):
	"""Create a new user, return the newly-created ID

	username: Name for the new user
	email: Email address (must be unique)
	password: Clear-text password
	hex_key: Confirmation key to verify email address
	"""
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

@cmdline
def confirm_user(id, hex_key):
    """Attempt to confirm a user's email address

    id: Numeric user ID (not user name or email)
    hex_key: Matching key to the one stored, else the confirmation fails
    """
    with _conn, _conn.cursor() as cur:
        cur.execute("UPDATE users SET status = 1, hex_key = '' WHERE id = %s AND hex_key = %s RETURNING username, email", (id, hex_key))
        try:
                return cur.fetchone()[0]
        except TypeError:
                return [None, None]
                
def test_reset_permissions(id, hex_key):
    with _conn, _conn.cursor() as cur:
        cur.execute("SELECT id, username, email FROM users WHERE id = %s AND hex_key = %s", (id, hex_key))
        try:
                return cur.fetchone()
        except TypeError:
                return [None, None]

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
		if len(rows)!=1: return "There is already an account for that email."
		cur.execute("update users set password=%s where id=%s", (pwd, rows[0][0]))
		
def check_db_for_user(user_or_email):
	"""Change a user's password (administratively) - returns None on success, or error message"""
	user_or_email = user_or_email.lower()
	with _conn, _conn.cursor() as cur:
		cur.execute("SELECT id, status FROM users WHERE username=%s OR email=%s", (user_or_email, user_or_email))
		rows=cur.fetchall()
		print(rows)
		if not len(rows)>=1: return "No account found."
		else: return "There is already an account for that email."

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

def hex_user_password(email, hex_key):
        """Return username and id that matches email."""
	with _conn, _conn.cursor() as cur:
		cur.execute("UPDATE users set hex_key = %s WHERE email=%s RETURNING username, id", (hex_key, email))
		row = cur.fetchone()
		return row or (None, 0)

def reset_user_password(id, hex_key, password):
    with _conn, _conn.cursor() as cur:
        salt = os.urandom(16)
        hash = hashlib.sha256(salt+password).hexdigest()
        pwd = salt.encode("hex")+"-"+hash
        cur.execute("update users set password=%s, hex_key='' where id=%s and hex_key=%s", (pwd, id, hex_key))

def get_analysis(id):
	with _conn, _conn.cursor() as cur:
		cur.execute("select analysis from tracks where id=%s", (id,))
		return cur.fetchone()[0]

def save_analysis(id, analysis):
	with _conn, _conn.cursor() as cur:
		cur.execute("update tracks set analysis=%s where id=%s", (analysis, id))

@cmdline
def importmp3(filename, submitter="Bulk import", submitteremail="bulk@import.invalid"):
	"""Bulk-import MP3 files into the appension database

	filename+: MP3 file(s) to import
	--submitter: Name of submitter
	--submitteremail: Email address of submitter
	"""
	# Build up a form-like dictionary for the info mapping. This is the downside of
	# the breaching of encapsulation in database.create_track().
	info = {"SubmitterName": [submitter], "Email": [submitteremail]}
	for fn in filename:
		print("Importing %s"%fn)
		with open(fn, "rb") as f: data = f.read()
		id = database.create_track(data, os.path.split(fn)[-1], info)
		print("Saved as track #%d."%id)

@cmdline
def tables(confirm=False):
	"""Update tables based on create_table.sql

	--confirm: If omitted, will do a dry run.
	"""
	tb = None; cols = set(); coldefs = []
	with _conn, _conn.cursor() as cur:
		def finish():
			if cols: coldefs.extend("drop "+col for col in cols)
			if tb and coldefs:
				if is_new: query = "create table "+tb+" ("+", ".join(coldefs)+")"
				else: query = "alter table "+tb+" add "+", add ".join(coldefs)
				if confirm: cur.execute(query)
				else: print(query)
		for line in open("create_table.sql"):
			line = line.rstrip()
			if line == "" or line.startswith("--"): continue
			# Flush-left lines are table names
			if line == line.lstrip():
				finish()
				tb = line; cols = set(); coldefs = []
				cur.execute("select column_name from information_schema.columns where table_name=%s", (tb,))
				cols = {row[0] for row in cur}
				is_new = not cols
				continue
			# Otherwise, it should be a column definition, starting (after whitespace) with the column name.
			colname, defn = line.strip().split(" ", 1)
			if colname in cols:
				# Column already exists. Currently, we assume there's nothing to change.
				cols.remove(colname)
			else:
				# Column doesn't exist. Add it!
				# Note that we include a newline here so that a comment will be properly terminated.
				# If you look at the query, it'll have all its commas oddly placed, but that's okay.
				coldefs.append("%s %s\n"%(colname,defn))
		finish()

@cmdline
def testfiles():
	"""Test all audio files"""
	import pyechonest.track
	for file in get_many_mp3(status=0):
		if file.track_details['length'] < 700:
			print("Name: {} Length: {}".format(file.filename, file.track_details['length']))
			# TODO: Should this be pyechonest.track.track_from_filename?
			track = track.track_from_filename('audio/'+file.filename, force_upload=True)
			print(track.id)
		else:
			print("BIG ONE - Name: {} Length: {}".format(file.filename, file.track_details['length']))

if __name__ == "__main__": cmdline.main()
