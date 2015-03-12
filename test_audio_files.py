import fore.apikeys
import fore.mixer
import fore.database

for file in fore.database.get_many_mp3():
	print(file.filename)
	stream = fore.mixer.LocalAudioStream('audio/'+file.filename)

