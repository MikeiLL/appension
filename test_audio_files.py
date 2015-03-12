import fore.apikeys
import fore.mixer
import fore.database
import pyechonest.track

for file in fore.database.get_many_mp3(status=0):
	if file.track_details['length'] < 700:
		print("Name: {} Length: {}".format(file.filename, file.track_details['length']))
		track = track.track_from_filename('audio/'+file.filename, force_upload=True)
		print(track.id)
	else:
		print("BIG ONE - Name: {} Length: {}".format(file.filename, file.track_details['length']))
		

