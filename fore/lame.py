try: from Queue import Queue # Py2
except ImportError: from queue import Queue # Py3
import subprocess
import threading
import traceback
import logging
import numpy
import time

log = logging.getLogger(__name__)

"""
	Quick and dirty, frame-aware MP3 encoding bridge using LAME.
	About 75% of the speed of raw LAME. Pass PCM data to the Lame class,
	get back (via callback, queue or file) MP3 frames. Supports real-time
	encoding or blocking for the length of the audio stream - useful for
	an MP3 server, or something else real time, for example.
"""

"""
Some important LAME facts used below:
	Each MP3 frame is identifiable by a header.
	This header has, essentially:
		"Frame Sync"            11 1's (i.e.: 0xFF + 3 bits)
		"Mpeg Audio Version ID" should be 0b11 for MPEG V1, 0b10 for MPEG V2
		"Layer Description"     should be 0b11
		"Protection Bit"        set to 1 by Lame, not protected
		"Bitrate index"         0000 -> free
								0001 -> 32 kbps
								0010 -> 40 kbps
								0011 -> 48 kbps
								0100 -> 56 kbps
								0101 -> 64 kbps
								0110 -> 80 kbps
								0111 -> 96 kbps
								1000 -> 112 kbps
								1001 -> 128 kbps
								1010 -> 160 kbps
								1011 -> 192 kbps
								1100 -> 224 kbps
								1101 -> 256 kbps
								1110 -> 320 kbps
								1111 -> invalid

	Following the header, there are always SAMPLES_PER_FRAME samples of audio data.
	At our constant sampling frequency of 44100, this means each frame
	contains exactly .026122449 seconds of audio.
"""

BITRATE_TABLE = [
	0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, None
]
SAMPLERATE_TABLE = [
	44100, 48000, 32000, None
]
HEADER_SIZE = 4
SAMPLES_PER_FRAME = 1152


def avg(l):
	return sum(l) / len(l)


def frame_length(header):
	bitrate = BITRATE_TABLE[ord(header[2]) >> 4]
	sample_rate = SAMPLERATE_TABLE[(ord(header[2]) & 0b00001100) >> 2]
	padding = (ord(header[2]) & 0b00000010) >> 1
	return int((float(SAMPLES_PER_FRAME) / sample_rate)
			   * ((bitrate / 8) * 1000)) + padding

def synchsafe(n):
	"""Return four bytes as synchsafe encoded version of the 28-bit number n."""
	# TODO: Simplify/optimize this.
	return str(bytearray([n>>21,(n>>14)&127,(n>>7)&127,n&127]))

class Lame(threading.Thread):
	"""
		Live MP3 streamer. Currently only works for 16-bit, 44.1kHz stereo input.
	"""
	safety_buffer = 30  # seconds
	input_wordlength = 16
	samplerate = 44100
	channels = 2
	preset = "-V3"

	#   Time-sensitive options
	real_time = False       #   Should we encode in 1:1 real time?
	block = False           #   Regardless of real-time, should we block
							#   for as long as the audio we've encoded lasts?

	stream_chunk_size = samplerate // 8
	data = None

	def __init__(self, callback=None, ofile=None, oqueue=None, syncqueue=None):
		threading.Thread.__init__(self)

		self.lame = None
		self.buffered = 0
		self.lame_input_length = 0
		self.in_samples = 0
		self.out_samples = 0
		self.delta = 0
		self.oqueue = oqueue
		self.syncqueue = syncqueue
		self.ofile = ofile
		self.callback = callback

		self.markers = []
		self.finished = False
		self.sent = False
		self.ready = threading.Semaphore()
		self.encode = threading.Semaphore()
		self.setDaemon(True)

		self.__write_queue = Queue()
		self.__write_thread = threading.Thread(target=self.__lame_write)
		self.__write_thread.setDaemon(True)
		self.__write_thread.start()

	@property
	def pcm_datarate(self):
		return self.samplerate * self.channels * (self.input_wordlength / 8)

	def add_pcm(self, data, marker=None):
		"""
		Expects PCM data in the form of a NumPy array,
		or an AudioRenderable that will be sliced according to the start and end.

		"""
		print("Lame::add_pcm: %r"%data)
		if self.lame.returncode is not None:
			return False
		if marker: self.markers.append((self.in_samples, marker))
		self.encode.acquire()
		if isinstance(data, numpy.ndarray):
			samples = len(data)
		else:
			samples = data.samples
		self.__write_queue.put(data)
		self.in_samples += samples
		put_time = time.time()
		if self.buffered >= self.safety_buffer:
			self.ready.acquire()
		done_time = time.time()
		if self.block and not self.real_time:
			delay = (samples / float(self.samplerate)) \
					- (done_time - put_time) \
					- self.safety_buffer
			time.sleep(delay)
		return True

	def __lame_write(self):
		while not self.finished:
			try:
				data = self.__write_queue.get()
				if data is None:
					break
				if isinstance(data, numpy.ndarray):
					self.buffered += len(data) / self.channels \
											* (self.input_wordlength / 8)
					try:
						data.tofile(self.lame.stdin)
					except IOError:
						log.error("Could not write to lame!")
						self.finished = True
						break
				else:
					try:
						tmp = 0
						for chunk in data.render(self.stream_chunk_size):
							if not chunk: continue # hacky hack
							try:
								samples = len(chunk)
								self.buffered += samples
								self.lame_input_length += samples
								tmp += samples
								chunk.tofile(self.lame.stdin)
							except IOError:
								log.error("Could not write to lame!")
								self.finished = True
								break
						self.delta += tmp - data.samples
						log.debug("Current delta: %d samples.", self.delta)
						#   Note: this delta will cause drift of 1 second/month.
						#   TODO: Fix it. Eventually.
					except Exception:
						log.error("Couldn't render segment due to:\n%s",
								traceback.format_exc())
			except Exception:
				log.critical("Failed to write to Lame:\n%s",
							 traceback.format_exc())
			finally:
				self.encode.release()
		log.info("Encoder finishing!")

	#   TODO: Extend me to work for all samplerates
	def start(self, *args, **kwargs):
		# TODO: Optionally run this with nice(1) for use-cases that don't require real-time processing
		# call = ["nice", "lame"]
		call = ["lame", "-r"]
		if self.input_wordlength != 16:
			call.extend(["--bitwidth", str(self.input_wordlength)])
		call.extend(self.preset.split())
		call.extend(["-", "-"])
		self.lame = subprocess.Popen(
			call,
			stdin=subprocess.PIPE,
			stdout=subprocess.PIPE,
			stderr=subprocess.PIPE
		)
		threading.Thread.start(self, *args, **kwargs)

	def ensure_is_alive(self):
		if self.finished:
			return False
		if self.is_alive():
			return True
		try:
			self.start()
			return True
		except Exception:
			return False

	def run(self, *args, **kwargs):
		try:
			last = None
			lag = 0
			while True:
				timing = float(SAMPLES_PER_FRAME) / self.samplerate

				header = self.lame.stdout.read(HEADER_SIZE)
				if len(header) == HEADER_SIZE:
					frame_len = frame_length(header) - HEADER_SIZE
					frame = self.lame.stdout.read(frame_len)
					buf = header + frame
					if len(frame) == frame_len:
						self.buffered -= SAMPLES_PER_FRAME
				else:
					buf = header

				if self.buffered < (self.safety_buffer * self.samplerate):
					self.ready.release()
				if len(buf):
					self.out_samples += SAMPLES_PER_FRAME
					if self.ofile:
						self.ofile.write(buf)
						self.ofile.flush()
					if self.callback:
						self.callback(False)
					if self.markers and self.markers[0][0] <= self.out_samples:
						# NOTE: This causes some players to glitch out badly, so this whole
						# section of code is never actually called (add_pcm is never given
						# a marker to store). If, in the future, this begins to be useful,
						# consider reenabling it.
						msg = self.markers.pop(0)[1]
						log.info("Adding marker: %r", msg)
						if isinstance(msg, unicode): msg=msg.encode("utf-8")
						msg = "\3" + msg # Prepend the UTF-8 encoding marker. If msg was already bytes, it MUST be valid UTF-8.
						frame = "TIT2"+synchsafe(len(msg))+"\0\0"+msg;
						self.oqueue.put("ID3\3\0\0"+synchsafe(len(frame))+frame)
					if self.oqueue:
						self.oqueue.put(buf)
					if self.real_time and self.sent:
						now = time.time()
						if last:
							delta = (now - last - timing)
							lag += delta
							if lag < timing:
								time.sleep(max(0, timing - delta))
						last = now
					self.sent = True
				else:
					if self.callback:
						self.callback(True)
					break
			self.lame.wait()
		except Exception:
			log.error(traceback.format_exc())
			self.finish()
			raise

	def finish(self):
		"""
			Closes input stream to LAME and waits for the last frame(s) to
			finish encoding. Returns LAME's return value code.
		"""
		if self.lame:
			self.__write_queue.put(None)
			self.encode.acquire()
			self.lame.stdin.close()
			self.join()
			self.finished = True
			return self.lame.returncode
		return -1


if __name__ == "__main__":
	import wave
	f = wave.open("test.wav")
	a = numpy.frombuffer(f.readframes(f.getnframes()),
						 dtype=numpy.int16).reshape((-1, 2))

	s = time.time()
	print("Encoding test.wav to testout.mp3...")
	encoder = Lame(ofile=open('testout.mp3', 'w'))
	encoder.safety_buffer = 30
	encoder.start()
	encoder.add_pcm(a)
	encoder.finish()
	s = time.time() - s
	print("Took %2.2fs" % s)
