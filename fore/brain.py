import sys
import time
import config
import apikeys
import logging
import traceback
from cube import emit
from timer import Timer
from requests import HTTPError
import database


log = logging.getLogger(__name__)
test = 'test' in sys.argv

magic_log = open("magic.log", "w")

def getIndexOfId(l, value):
    for pos, t in enumerate(l):
        if t.id == value:
            return pos

    # Matches behavior of list.index
    raise ValueError("list.index(x): x not in list")

def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]

class Magic_Str(str):
	"""Callable string. If called, it returns itself with () appended.
	It's also able to be treated as an integer (it'll be zero).
	"""
	def __call__(self, *args, **kw):
		print >>magic_log, self+"()"
		return self+"()"
	def __int__(self): return 0
	def __index__(self): return 0

class Magic_Anything(object):
	"""
	Magic class that has every possible method/attribute
	
	Actually, there are no methods, per se. When any attribute is sought,
	a Magic_Str() will be returned.
	"""
	def __init__(self, id):
		self._id = id
	def __repr__(self):
		return "Magic_Anything(" + repr("Brain#" + str(self._id)) + ")"
	def __getattribute__(self, name):
		if name == "id": return self._id
		if name.startswith("_"): return object.__getattribute__(self, name)
		print >>magic_log, repr(self) + "." + name
		return Magic_Str(repr(self) + "." + name)

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
