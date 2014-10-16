import sys
import tsp
import time
import shlex
import config
import apikeys
import difflib
import logging
import traceback
from cube import emit
from timer import Timer
from requests import HTTPError
from database import Database


log = logging.getLogger(__name__)
test = 'test' in sys.argv

def getIndexOfId(l, value):
    for pos, t in enumerate(l):
        if t.id == value:
            return pos

    # Matches behavior of list.index
    raise ValueError("list.index(x): x not in list")


class Criteria(object):
    WEIGHT = 1

    def __init__(self):
        self.update_weight()

    def __call__(self, a, b):
        try:
            d = max(min(self.diff(a, b), 1.0), 0.0)
        except Exception:
            d = None
        if d is not None:
            return (d * self.WEIGHT, self.WEIGHT)
        else:
            return (0, 0)

    def precompute(self, track):
        pass

    def postcompute(self, track):
        pass

    def update_weight(self):
        try:
            self.WEIGHT = getattr(config,
                                  self.__class__.__name__.lower() + "_weight")
        except Exception:
            log.warning("Could not update weight for criteria \"%s\":\n%s",
                        self.__class__.__name__, traceback.format_exc())

    def diff(self, a, b):
        raise NotImplementedError()


class Tag(Criteria):
    def precompute(self, track):
        try:
            track.obj['_tags'] = set(shlex.split(track.tag_list))
        except ValueError:
            track.obj['_tags'] = set()

    def postcompute(self, track):
        del track.obj['_tags']

    def diff(self, a, b):
        """
        Return the number of tags that are uncommon between the two tracks.
        """
        if a._tags and b._tags:
            return (len(a._tags | b._tags) - len(a._tags & b._tags)) / 10.0
        else:
            return None


class Tempo(Criteria):
    def diff(self, a, b):
        a = a.tempo if hasattr(a, 'tempo') else a.bpm
        b = b.tempo if hasattr(b, 'tempo') else b.bpm
        if a < 200 and b < 200:
            return abs(a - b) / 100.0


class Length(Criteria):
    def diff(self, a, b):
        return abs(a.duration - b.duration) / 100.0


class Spread(Criteria):
    def diff(self, a, b):
        return int(a.user['username'] == b.user['username'])


class Genre(Criteria):
    def diff(self, a, b):
        r = difflib.SequenceMatcher(a=a.genre.lower(),
                                    b=b.genre.lower()).ratio()
        return (1.0 - r)


class Danceability(Criteria):
    def diff(self, a, b):
        if hasattr(a, 'danceability') and hasattr(b, 'danceability'):
            return abs(a.danceability - b.danceability)


class Energy(Criteria):
    def diff(self, a, b):
        if hasattr(a, 'energy') and hasattr(b, 'energy'):
            return abs(a.energy - b.energy)


class Loudness(Criteria):
    def diff(self, a, b):
        if hasattr(a, 'loudness') and hasattr(b, 'loudness'):
            return abs(a.loudness - b.loudness) / 10.0


criteria = [Tag(), Tempo(), Length(), Spread(), Genre(), Danceability(), Energy(), Loudness()]


def distance(a, b):
    values = [c(a, b) for c in criteria]
    return float(sum([n for n, _ in values])) /\
           float(sum([d for _, d in values]))


def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def valid(track, user_blacklist=set(), tag_blacklist=set()):
    return (track.streamable or track.downloadable) \
            and track.duration < (config.max_track_length * 1000) \
            and track.duration > (config.min_track_length * 1000) \
            and not track.user['username'] in user_blacklist \
            and track._tags.isdisjoint(tag_blacklist)


def cull(tracks):
    u = set(config.blacklist['user'])
    t = set(config.blacklist['tag'])
    for track in tracks:
        for criterion in criteria:
            criterion.precompute(track)
    tracks = filter(lambda x: valid(x, u, t), tracks)
    tracks = list(set(tracks))
    return tracks


def get_immediate_tracks(db):
    try:
        success = False
        for track in open(config.immediate_track_list):
            try:
                res = client.get('/tracks/%d' % int(track))
                for criterion in criteria:
                    criterion.precompute(res)
                res = db.merge(res)
                for criterion in criteria:
                    criterion.postcompute(res)
                success = True
                yield res
            except Exception as e:
                log.warning("Couldn't add immediate track \"%s\" due to %s!",
                            track, e)
        if success:
            tracklist = open(config.immediate_track_list, 'w')
            tracklist.write("")
            tracklist.close()
    except Exception as e:
        log.error("Got %s when trying to fetch immediate tracks!", e)
        yield []


def get_force_mix_tracks(db):
    try:
        for track in open(config.force_mix_track_list):
            try:
                res = client.get('/tracks/%d' % int(track))
                for criterion in criteria:
                    criterion.precompute(res)
                res = db.merge(res)
                yield res
            except Exception as e:
                log.warning("Couldn't add forced track \"%s\" due to %s!",
                            track, e)
    except Exception as e:
        log.error("Got %s when trying to fetch forced tracks!", e)
        yield []

class Magic_Str(str):
	"""Callable string. If called, it returns itself with () appended.
	It's also able to be treated as an integer (it'll be zero).
	"""
	def __call__(self, *args, **kw):
		return self+"()"
	def __int__(self): return 0
	def __index__(self): return 0

class Magic_Anything(object):
	"""
	Magic class that has every possible method/attribute
	
	Actually, there are no methods, per se. When any attribute is sought,
	a Magic_Str() will be returned.
	"""
	def __init__(self, name):
		self._name = name
	def __repr__(self):
		return "Magic_Anything(" + repr(self._name) + ")"
	def __getattribute__(self, name):
		if name.startswith("_"): return object.__getattribute__(self, name)
		return Magic_Str(repr(self) + "." + name)

def generate():
    try:
        tracks = []
        last = []
        wait = 2  # seconds
        d = Database()
        counter = 0
        while True:
            # TODO: Fetch from PostgreSQL
            counter += 1
            yield Magic_Anything("Brain#" + str(counter))

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
