import time
import base64
import logging
import traceback
from metadata import Metadata

log = logging.getLogger(__name__)


def generate(iq, first_frame):
    log.info("Info generator waiting on first frame...")
    first_frame.acquire()
    stime = time.time()
    log.info("Info generator got first frame! Start time: %2.2f", stime)
    samples = 0L
    while True:
        try:
            action = iq.get()
            action['time'] = stime + (samples / 44100.0)
            samples += action['samples']
            action['unicode'] = u"\x96\x54"
            yield action
        except Exception:
            log.error("Could not get action!\n%s", traceback.format_exc())
