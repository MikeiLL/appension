#!/usr/bin/env python
# encoding: utf=8

"""
capsule_support.py

Created by Tristan Jehan and Jason Sundram.
"""
import logging
from action import Crossfade as cf
from action import Playback as pb

log = logging.getLogger(__name__)

LOUDNESS_THRESH = -8

def last_viable(track):
	for seg in reversed(track.analysis.segments):
		if seg.loudness_max > -60:
			#time of last audible piece of track
			return seg.start + seg.duration
			
def first_viable(track):
	for seg in track.analysis.segments:
		if seg.loudness_max > -60:
			#time of first audible segment of track
			return seg.start
			

					
def end_trans(track, beats_to_mix = 0):
	"""
	Return tuples with times to be sent to Playback and Crossmix objects
	"""
	end_viable = last_viable(track)
	try:
		avg_duration = sum([b.duration for b in track.analysis.tatums[-16:]]) / 16
	except IndexError:
		avg_duration = sum([b.duration for b in track.analysis.segments[-8:]]) / 8
	#How much of the track are we returning - adjust for beats to mix?
	half_way_point = len(track.analysis.segments) / 2
	start = track.analysis.segments[half_way_point].start
	if beats_to_mix > 0:
		#if we're crossfading, playback ends at first beat of crossfade
		playback_end = end_viable - (avg_duration * beats_to_mix)
		final =  int(beats_to_mix) #count tatums from end of tatum list

	else:
		#if we're not crossfading playback to end, final beat being last tatum
		playback_end = end_viable
		final = 1
		
	try:
		track.analysis.tatums[-1]
	except IndexError:
		# if no tatums play through end of track
		final_segments = {"subsequent_beat": track.analysis.segments[-final].start}
		final_segments["playback_start"] = start
		final_segments["playback_duration"] = playback_end - final_segments["playback_start"]
		final_segments["mix_start"] = final_segments['subsequent_beat']
		final_segments["mix_duration"] = end_viable - final_segments['subsequent_beat']
		final_segments["avg_duration"] = avg_duration
		return final_segments

	final_segments = {"subsequent_beat": track.analysis.tatums[-final].start}
	while final_segments['subsequent_beat'] < playback_end:
		#get first "beat" following end of playback
		final_segments['subsequent_beat'] += avg_duration

	final_segments["playback_start"] = start
	final_segments["playback_duration"] = playback_end - final_segments["playback_start"]
	final_segments["mix_start"] = final_segments['subsequent_beat']
	final_segments["mix_duration"] = end_viable - final_segments['subsequent_beat']
	final_segments["avg_duration"] = avg_duration

	return final_segments
	
def db_2_volume(loudness):
		return (1.0 - LOUDNESS_THRESH * (LOUDNESS_THRESH - loudness) / 100.0)
	
start_point = {"cursor": 0}
	
def managed_transition(track1, track2):
    log.info("now we got track1: %s and track2: %s", track1._metadata.track_details['artist'], track2._metadata.track_details['artist'])
    for track in [track1, track2]:
        loudness = track.analysis.loudness
        track.gain = db_2_volume(loudness)

    xfade = float(track1._metadata.track_details['xfade'])
    itrim = float(track2._metadata.track_details['itrim'])
    otrim = float(track1._metadata.track_details['otrim'])
    t1_length = float(track1._metadata.track_details['length'])
    t2_length = float(track2._metadata.track_details['length'])
    t2_otrim = float(track2._metadata.track_details['otrim'])
    '''We would start at zero, but make it first audible segment'''
    t2start = first_viable(track2)
    t2start = t2start + float(track2._metadata.track_details['itrim'])
    
    if xfade == 0:
    
        log.warning("""
        So we want to play all of track 1 (%s), starting at point at which cursor last set which is %r.
Then we want to play track 2 (%s) for the entire length (%r) minus t2_otrim which is %r, minus 2 so we'll play it for
%r seconds. Cursor is currently at %r, and we'll now set it so the first viable segment of track2 (%r)
PLUS t2_length - t2_otrim - 2, so: %r.
        """, track1._metadata.track_details['artist'],  start_point['cursor'], track2._metadata.track_details['artist'], t2_length, t2_otrim, t2_length - t2_otrim - 2, start_point['cursor'], t2start, t2start + t2_length - t2_otrim - 2)
        
        times = end_trans(track1)
        if times["playback_duration"] - otrim < 0:
            raise Exception("You can't trim off more than 100%.")
        pb1 = pb(track1, start_point['cursor'], t1_length)
        pb2 = pb(track2, t2start, t2_length - t2_otrim - 2)
        start_point['cursor'] = t2start + t2_length - t2_otrim - 2
        return [pb1, pb2]
    else:
        
        '''offset between start and first theoretical beat.'''
        t2offset = lead_in(track2)
        times = end_trans(track1, beats_to_mix=xfade)
        log.warning(str(times))
        log.warning("""
        This time we to play track 1 (%s), starting at last cursor time which is %r, for the playback duration (%r), minus the offset """ \
        + """returned by lead_in: %r.
Then play the crossfade: track1 starting at playback start + duration minus offset: %r, mixed with track 2 (%s) starting 
at %r (first viable plus trim) for a duration of %r (from mix_trans). And we reset the cursor to: %r.
        """, track1._metadata.track_details['artist'], 
        start_point['cursor'],
        times["playback_duration"],
        t2offset,
        times["playback_start"] + times["playback_duration"] - t2offset,
        track2._metadata.track_details['artist'],
        t2start,
        times["mix_duration"],
        t2start + times["mix_duration"]
        )
        
        log.info("times mix_duration is %r", times["mix_duration"])

        pb1 = pb(track1, start_point['cursor'], times["playback_duration"] - t2offset)
        pb2 = cf((track1, track2), (times["playback_start"] + times["playback_duration"] - t2offset, t2start), times["mix_duration"])
        start_point['cursor'] = t2start + times["mix_duration"]
        return [pb1, pb2]

def lead_in(track):
    """
    Return the time between start of track and first beat.
    """
    try:
        avg_duration = sum([b.duration for b in track.analysis.beats[:8]]) / 8
        earliest_beat = track.analysis.beats[0].start
    except IndexError:
        log.warning("No beats returned for track by %r", track._metadata.track_details['artist'])
        earliest_beat = track.analysis.segments[0].start
    while earliest_beat >= 0 + avg_duration:
        earliest_beat -= avg_duration
    offset = earliest_beat
    return offset