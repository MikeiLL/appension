'''
Extract MP3 metadata from MP3 file ID3 tags

'''

usage = '''
python id3info.py
'''
from mutagen.mp3 import MP3
import glob
import time
import psycopg2

def dbactions(track, cur):
	cur.execute("INSERT INTO tracks \
			(title, \
			filename, \
			artist) \
			VALUES (%s, %s, %s)",
		(track['TPE1'].text,
		track['TIT2'].text,
		track.filename[6:])
		)
	cur.execute("SELECT  \
			(id, \
			title, \
			filename, \
			artist) \
			FROM tracks \
			WHERE 'filename' \
			LIKE (%s)",
		(
		track.filename[6:],)
		)
	cur.fetchone()
	time.sleep(.3)
	return
		
def titles(files, cur):
	print(len(files))
	for file in files:
		track = MP3(file)
		try:
			dbactions(track, cur)		
			print("Inserting: {} - {} - {}".format(
				track['TPE1'].text, 
				track['TIT2'].text,
				track.filename[6:]))
		except KeyError:
			pass
	commit = raw_input("Commit?")
	if commit == 'y':
		conn.commit()
		cur.close()
		conn.close()
	else:
		rollback = raw_input("rollback?")
		if rollback == 'y':
			conn.rollback()
		print("Nothing commited")
		
if __name__ == "__main__":
	print("ID3 Process:")
	files = glob.glob('audio/*.mp3')
	conn = psycopg2.connect("dbname=mikekilmer")
	cur = conn.cursor()
	try:
		titles(files, cur)
	except IOError:
		print usage