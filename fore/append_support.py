#!/usr/bin/env python
# encoding: utf=8

"""
append_support.py

By Mike iLL / mZoo.org
Based on Capsule Support created by Tristan Jehan and Jason Sundram.
"""

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
	


