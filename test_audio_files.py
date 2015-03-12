import fore.apikeys
import fore.mixer
import fore.database
import pyechonest.track
pyechonest.track.track_from_md5.func_defaults=120,

for file in fore.database.get_many_mp3(status='all'):
	print("Name: {} Length: {}".format(file.filename, file.track_details.length))
	stream = fore.mixer.LocalAudioStream('audio/'+file.filename)

