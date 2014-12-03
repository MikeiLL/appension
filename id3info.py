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
	cur.execute("SELECT id FROM tracks WHERE filename = %s", (track.filename[6:],))
	if cur.fetchone():
		print("Skipping - already present in database.")
		return
	pic=next((k for k in track if k.startswith("APIC:")), None)
	pic = pic and track[pic].data
	if pic: print("length of pic: {}".format(len(pic)))

	cur.execute("INSERT INTO tracks \
			(artist, \
			title,	\
			filename, \
			artwork, \
			length \
			) \
			VALUES (%s, %s, %s, %s, %s)",
		(u', '.join(track['TPE1'].text),
		u', '.join(track['TIT2'].text),
		track.filename[6:],
		pic and memoryview(pic),
		track.info.length)
		)
	return
		
def titles(files, cur):
	print(len(files))
	for file in files:
		track = MP3(file)
		try:	
			print("Inserting: {} - {} - {} - {}".format(
				u", ".join(track['TPE1'].text), 
				u", ".join(track['TIT2'].text),
				track.filename[6:],
				track.info.length))
			dbactions(track, cur)	
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
	conn = psycopg2.connect("")
	cur = conn.cursor()
	try:
		titles(files, cur)
	except IOError:
		print usage
