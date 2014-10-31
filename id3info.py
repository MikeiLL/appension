'''
Extract MP3 metadata from MP3 file ID3 tags

'''

usage = '''
python id3info.py
'''
from mutagen.mp3 import MP3
import glob

def titles(files):
	print(len(files))
	for file in files:
		track = MP3(file)
		try:
			print("Track info is: {} - {} - {} - {}".format(
				track['TPE1'].text, 
				track['TIT2'].text,
				track['TALB'].text,
				track.filename[6:]))
		except KeyError:
			pass
		
if __name__ == "__main__":
	print("ID3 details:")
	files = glob.glob('audio/*.mp3')
	try:
		titles(files)
	except IOError:
		print usage