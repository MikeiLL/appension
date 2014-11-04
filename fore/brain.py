import sys
import time
import config
import apikeys
import logging
import traceback
from timer import Timer
from requests import HTTPError
import database


log = logging.getLogger(__name__)
test = 'test' in sys.argv

def getIndexOfId(l, value):
    for pos, t in enumerate(l):
        if t.id == value:
            return pos

    # Matches behavior of list.index
    raise ValueError("list.index(x): x not in list")

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

def generate():
    try:
        tracks = []
        last = []
        wait = 2  # seconds
        while True:
            tracks = database.get_many_mp3()
            # yield from tracks # if we were using Python 3.3+
            for track in tracks: yield track

    except Exception:
        print traceback.format_exc()
        log.critical("%s", traceback.format_exc())


def print_table(tracks):
    print "delta",
    for criterion in criteria:
        print "\t%s\t" % criterion.__class__.__name__,
    print "\tBPM\tTitle"

    for i in xrange(1, len(tracks)):
        print "%2.2f" % distance(tracks[i], tracks[i - 1]),
        for criterion in criteria:
            print "\t%2.1f/%2.1f" % criterion(tracks[i], tracks[i - 1]),
        print "\t%2.1f" % ((tracks[i].tempo if hasattr(tracks[i], 'tempo') else tracks[i].bpm) or 0),
        print "\t", tracks[i].title, "by", tracks[i].user['username']

if __name__ == "__main__":
    print "Testing the BRAIN..."
    print "The brain returned:",next(generate())
