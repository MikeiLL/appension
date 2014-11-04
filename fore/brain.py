import logging
import traceback
import database

log = logging.getLogger(__name__)

def generate():
    try:
        while True:
            tracks = database.get_many_mp3()
            # yield from tracks # if we were using Python 3.3+
            for track in tracks: yield track

    except Exception:
        print traceback.format_exc()
        log.critical("%s", traceback.format_exc())
