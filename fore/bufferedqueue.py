"""
bufferedqueue.py

Subclass Queue.Queue and run as Daemon buffer to handle chunks of mp3 stream.

By PSobot.
"""
try: import Queue as queue # Py2
except ImportError: import queue # Py3
import multiprocessing
import threading


class BufferedReadQueue(queue.Queue):
	def __init__(self, lim=None):
		self.raw = multiprocessing.Queue(lim)
		self.__listener = threading.Thread(target=self.listen)
		self.__listener.setDaemon(True)
		self.__listener.start()
		queue.Queue.__init__(self, lim)

	def listen(self):
		try:
			while True:
				self.put(self.raw.get())
		except Exception:
			# ouch
			pass

	@property
	def buffered(self):
		return self.qsize()
