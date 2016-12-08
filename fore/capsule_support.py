#!/usr/bin/env python
# encoding: utf=8

"""
capsule_support.py

Created by Tristan Jehan and Jason Sundram.
"""
import logging
import numpy as np
from copy import deepcopy
from .action import Crossfade, Playback, Crossmatch, Fadein, Fadeout, humanize_time
from .utils import rows, flatten
import pandas.tslib
log = logging.getLogger(__name__)

# constants for now
X_FADE = 3
FADE_IN = 0.25
FADE_OUT = 6
MIN_SEARCH = 4
MIN_MARKERS = 2
MIN_ALIGN_DURATION = 3
LOUDNESS_THRESH = -8
FUSION_INTERVAL = .06    # this is what we use in the analyzer
AVG_PEAK_OFFSET = 0.025  # Estimated time between onset and peak of segment.


def display_actions():
	total = 0
	a = yield
	print
	while True:
		a = yield "%s\t  %s" % (humanize_time(total), unicode(a))
		total += a.duration
	print


def evaluate_distance(mat1, mat2):
	return np.linalg.norm(mat1.flatten() - mat2.flatten())


def upsample_matrix(m):
	""" Upsample matrices by a factor of 2."""
	r, c = m.shape
	out = np.zeros((2 * r, c), dtype=np.float32)
	for i in range(r):
		out[i * 2    , :] = m[i, :]
		out[i * 2 + 1, :] = m[i, :]
	return out


def upsample_list(l, rate=2):
	""" Upsample lists by a factor of 2."""
	if rate != 2:
		return l[:]
	# Assume we're an AudioQuantumList.

	def split(x):
		a = deepcopy(x)
		a.duration = x.duration / 2
		b = deepcopy(a)
		b.start = x.start + a.duration
		return a, b

	return flatten(map(split, l))


def average_duration(l):
	return sum([i.duration for i in l]) / float(len(l))


def equalize_tracks(tracks):

	def db_2_volume(loudness):
		return (1.0 - LOUDNESS_THRESH * (LOUDNESS_THRESH - loudness) / 100.0)

	for track in tracks:
		loudness = track.analysis.loudness
		track.gain = db_2_volume(loudness)

def is_valid(track, transition):
	markers = getattr(track.analysis, track.resampled['rate'])
	if len(markers) < 1:
		dur = track.duration
	else:
		dur = markers[-1].start + markers[-1].duration - markers[0].start
	return 2 * transition < dur


def get_central(analysis, member='segments'):
	""" Returns a tuple:
		1) copy of the members (e.g. segments) between end_of_fade_in and start_of_fade_out.
		2) the index of the first retained member.
	"""
	def central(s):
		# CJA 20161208: Fade doesn't exist as its own 'thing'. For now, we pretend there's none.
		# return analysis.end_of_fade_in <= s.start and (s.start + s.duration) < analysis.start_of_fade_out
		return True

	members = getattr(analysis, member)  # this is nicer than data.__dict__[member]
	ret = list(filter(central, members[:]))
	index = members.index(ret[0]) if ret else 0

	return ret, index


def get_mean_offset(segments, markers):
	if segments == markers:
		return 0

	index = 0
	offsets = []
	try:
		for marker in markers:
			ms = marker.start.total_seconds()
			while segments[index].start.total_seconds() < ms + FUSION_INTERVAL:
				offset = abs(ms - segments[index].start.total_seconds())
				if offset < FUSION_INTERVAL:
					offsets.append(offset)
				index += 1
	except IndexError:
		pass

	return np.average(offsets) if offsets else AVG_PEAK_OFFSET


def resample_features(data, rate='tatums', feature='timbre'):
	"""
	Resample segment features to a given rate within fade boundaries.
	@param data: analysis object.
	@param rate: one of the following: segments, tatums, beats, bars.
	@param feature: either timbre or pitch.
	@return A dictionary including a numpy matrix of size len(rate) x 12, a rate, and an index
	"""
	ret = {'rate': rate, 'index': 0, 'cursor': 0, 'matrix': np.zeros((1, 12), dtype=np.float32)}
	segments, ind = get_central(data.analysis, 'segments')
	markers, ret['index'] = get_central(data.analysis, rate)

	if len(segments) < 2 or len(markers) < 2:
		return ret

	# Find the optimal attack offset
	meanOffset = pandas.tslib.Timedelta(get_mean_offset(segments, markers), "s")
	tmp_markers = deepcopy(markers)
	START = pandas.tslib.Timedelta(0)

	# Apply the offset
	for m in tmp_markers:
		m.start -= meanOffset
		if m.start < START:
			m.start = START

	# Allocate output matrix, give it alias mat for convenience.
	mat = ret['matrix'] = np.zeros((len(tmp_markers) - 1, 12), dtype=np.float32)

	# Find the index of the segment that corresponds to the first marker
	index = next(i for i, x in enumerate(segments) if tmp_markers[0].start < x.start + x.duration)

	# Do the resampling
	try:
		for (i, m) in enumerate(tmp_markers):
			while segments[index].start + segments[index].duration < m.start + m.duration:
				dur = segments[index].duration
				if segments[index].start < m.start:
					dur -= m.start - segments[index].start

				C = min(dur / m.duration, 1)

				# hacky hack
				# mat[i, 0:12] += C * np.array(getattr(segments[index], feature))
				index += 1

			C = min((m.duration + m.start - segments[index].start) / m.duration, 1)
			# hacky hack
			# mat[i, 0:12] += C * np.array(getattr(segments[index], feature))
	except IndexError:
		pass  # avoid breaking with index > len(segments)

	return ret


def column_whiten(mat):
	""" Zero mean, unit variance on a column basis"""
	m = mat - np.mean(mat, 0)
	return m / np.std(m, 0)


def timbre_whiten(mat):
	if rows(mat) < 2:
		return mat
	m = np.zeros((rows(mat), 12), dtype=np.float32)
	m[:, 0] = mat[:, 0] - np.mean(mat[:, 0], 0)
	m[:, 0] = m[:, 0] / np.std(m[:, 0], 0)
	m[:, 1:] = mat[:, 1:] - np.mean(mat[:, 1:].flatten(), 0)
	m[:, 1:] = m[:, 1:] / np.std(m[:, 1:].flatten(), 0)  # use this!
	return m


