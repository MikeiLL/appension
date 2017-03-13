import time
import requests
SERVER = "http://infiniteglitch.net:81"

while True:
	s = requests.get(SERVER + "/status.json").json()
	print("Unplayed:", s["render_time"] - s["ts"])
	for t in s["tracks"]:
		print(t["id"], s["render_time"] - t["start_time"], t["details"]["artist"], t["details"]["length"])
	print("Lag:", t["start_time"] + t["details"]["length"] - s["render_time"])
	print("")
	time.sleep(2)
