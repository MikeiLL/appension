import socket
import time
import sys
from lame import frame_length

# Note: "listen" here is from a human's POV, involving listening to music.
# It does not listen in the TCP sense - it connects to the existing server
# and represents the simplest and dumbest client. Good for load testing (in
# theory - MikeILL/Rosuav so far unable to get this working). Comments have
# been added to attempt to elucidate its workings, but may be wrong. There
# were previously virtually no comments, alas.

def listen(host, port, f="all.mp3"):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	connect = "GET /%s HTTP/1.1\r\n\r\nHost: %s\r\n\r\n" % (f, host)
	print connect
	s.send(connect)

	at = None
	times = []

	off = 0
	while True:
		start = s.recv(512)
		if "\xFF\xFB" in start: # Locate the MP3 header sync word (which technically is 12 bits, but the next four - the B - are usually dependable too)
			i = start.index("\xFF\xFB")
			off = len(start) - i - 4
			start = start[i:i + 4]
			break
		else:
			print("start: %r"%start) # Warning, spammy
			break

	while True:
		if start:
			print("we have start")
			header = start
			start = None
		else:
			header = s.recv(4)
			off = 0
		if not len(header):
			break
		try:
			flen = frame_length(header)
			if (flen - 4 - off) < 0: continue
		except Exception: # Bad except! Bad, bad except! Well, at least it isn't completely bare...
			continue
		data = s.recv(flen - 4 - off)
		got = time.time()
		if not data: break
		if at:
			times.append(got - at)
			avg = ((1152 / 44100.0) / (sum(times) / len(times)))
			print "Frame (%d bytes, %2.5fs) received after %2.5fs\t(%2.2fx)\tAvg: %fx" % \
					(len(data), 1152 / 44100.0, got - at,  (1152 / 44100.0) / (got - at), avg)
			times = times[:383]  # number of frames in the past 10 seconds [original comment, s/be trustworthy]
		at = got

if __name__ == "__main__":
	if len(sys.argv) > 2:
		listen(sys.argv[1], int(sys.argv[2]))
	else:
		listen("localhost", 8888)
