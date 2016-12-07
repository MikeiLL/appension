import time
import base64
import logging
import traceback

log = logging.getLogger(__name__)


def generate(iq, first_frame, handler):
	log.info("Info generator waiting on first frame...")
	first_frame.acquire()
	stime = time.time()
	log.info("Info generator got first frame! Start time: %2.2f", stime)
	samples = 0
	while True:
		try:
			action = iq.get()
			action['time'] = stime + (samples / 44100.0)
			samples += action['samples']
			'''for k, v in enumerate(action):
				print("Action contains: ", k, v)
			0,1,2,3,4 action, duration, tracks, samples, time'''
			'''for t in action['tracks']:
			for k in enumerate(t):
				print("It be: {}".format(k))
			0,1,2 start, end, metadata
			'''
			action['unicode'] = u"\x96\x54"
			handler.add(action)
		except Exception:
			log.error("Could not get action!\n%s", traceback.format_exc())
