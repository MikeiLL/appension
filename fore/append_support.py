#!/usr/bin/env python
# encoding: utf=8

"""
append_support.py

By Mike iLL / mZoo.org
Based on Capsule Support created by Tristan Jehan and Jason Sundram.
"""

import numpy as np
from copy import deepcopy
from action import Crossfade, Playback, Crossmatch, Fadein, Fadeout, humanize_time
from utils import rows, flatten

# constants for now
X_FADE = 1
FADE_IN = 0.25
FADE_OUT = 6
MIN_SEARCH = 4
MIN_MARKERS = 2
MIN_ALIGN_DURATION = 3
LOUDNESS_THRESH = -8
FUSION_INTERVAL = .06   # this is what we use in the analyzer
AVG_PEAK_OFFSET = 0.025 # Estimated time between onset and peak of segment.

# TODO: this should probably be in actions?
def display_actions(actions):
	total = 0
	print()
	for a in actions:
		#print("%s\t  %s" % (humanize_time(total), unicode(a)))
		total += a.duration
	print()

def evaluate_distance(mat1, mat2):
	return np.linalg.norm(mat1.flatten() - mat2.flatten())

def upsample_matrix(m):
	""" Upsample matrices by a factor of 2."""
	r, c = m.shape
	out = np.zeros((2*r, c), dtype=np.float32)
	for i in xrange(r):
		out[i*2  , :] = m[i, :]
		out[i*2+1, :] = m[i, :]
	return out

def upsample_list(l, rate=2):
	""" Upsample lists by a factor of 2."""
	if rate != 2: return l[:]
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

def align(track1, track2, mat1, mat2):
	""" Constrained search between a settled section and a new section.
		Outputs location in mat2 and the number of rows used in the transition.
	"""
	# Get the average marker duration.
	marker1 = average_duration(getattr(track1.analysis, track1.resampled['rate'])[track1.resampled['index']:track1.resampled['index']+rows(mat1)])
	marker2 = average_duration(getattr(track2.analysis, track2.resampled['rate'])[track2.resampled['index']:track2.resampled['index']+rows(mat2)])

	def get_adjustment(tr1, tr2):
		"""Update tatum rate if necessary"""
		dist = np.log2(tr1 / tr2)
		if  dist < -0.5: return (1, 2)
		elif dist > 0.5: return (2, 1)
		else:            return (1, 1)
	
	rate1, rate2 = get_adjustment(marker1, marker2)
	if rate1 == 2: mat1 = upsample_matrix(mat1)
	if rate2 == 2: mat2 = upsample_matrix(mat2)
	
	# Update sizes.
	rows2 = rows(mat2)
	rows1 = min( rows(mat1), max(rows2 - MIN_SEARCH, MIN_MARKERS)) # at least the best of MIN_SEARCH choices
	
	# Search for minimum.
	def dist(i):
		return evaluate_distance(mat1[0:rows1,:], mat2[i:i+rows1,:])
	
	min_loc = min(xrange(rows2 - rows1), key=dist)
	min_val = dist(min_loc)
	print("Min_loc: %r" % min_loc)
	print("Min_val: %r" % min_val)
	# Let's make sure track2 ends its transition on a regular tatum.
	if rate2 == 2 and (min_loc + rows1) & 1: 
		rows1 -= 1
		print("Rows, rate1 and rate2 are: %r %r %sr" % (rows1, rate1, rate2))
	return min_loc, rows1, rate1, rate2

def equalize_tracks(tracks):
	
	def db_2_volume(loudness):
		return (1.0 - LOUDNESS_THRESH * (LOUDNESS_THRESH - loudness) / 100.0)
	
	for track in tracks:
		loudness = track.analysis.loudness
		track.gain = db_2_volume(loudness)

def abridge(track):
	"""
	remove track segments between COUNT bars at start and end
	"""
	def cut(track, count=4):
		start = 0
		end = len(track.analysis.segments)
		print("Original number of segments", len(track.analysis.segments))
		for segment in track.analysis.segments:
			if start < track.analysis.bars[count].end:
				start += 1
			elif segment.start >= track.analysis.bars[-count].start:
				end -= 1
		print("Removing segments", start, "-", end)
		del track.analysis.segments[start:end]
		print("Abridged number of segments", len(track.analysis.segments))
	
	if track.analysis.bars:
		track = cut(track, 4)

				
def trim_silence(tracks):

	def trim(segments):
		return [seg for seg in track.analysis.segments if seg.loudness_max > -60]
		
	for track in tracks:
		track = trim(track.analysis.segments)
		return track

def pre_post(beats, bars):
	"""
	return number of beats before first and after last bar
	"""
	beats_in = 0
	beats_out = 0
	for beat in beats:
		if beat < bars[0].start:
			beats_in += 1
		if beat.start >= bars[-1].end:
			beats_out += 1
	return (beats_in, beats_out)

def is_valid(track, inter, transition):
	markers = getattr(track.analysis, track.resampled['rate'])
	if len(markers) < 1:
		print("Length margers GT 1:", len(markers))
		dur = track.duration
	else:
#        dur = track.duration
		print("Length Markers LT 1:", markers[-1].start, " + ", markers[-1].duration, " - ", markers[0].start)
		dur = markers[-1].start + markers[-1].duration - markers[0].start
	print("is_valid return", inter, "+ 2 *", transition, " < ", dur, inter + 2 * transition < dur)
	return inter + 2 * transition < dur

def appension(track1):
	print(track1.filename)
	return [track1.analysis.segments]
	


