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
    """Return end time of last audible segment"""
    for seg in reversed(track.analysis.segments):
        if seg.loudness_max > -60:
            #time of last audible piece of track
            return seg.start + seg.duration
			
def first_viable(track):
    """Return start time of first audible segment"""
    for seg in track.analysis.segments:
        if seg.loudness_max > -60:
            #time of first audible segment of track
            return seg.start
	
def db_2_volume(loudness):
		return (1.0 - LOUDNESS_THRESH * (LOUDNESS_THRESH - loudness) / 100.0)
		
def avg_end_duration(track):
    try:
        return sum([b.duration for b in track.analysis.tatums[-16:]]) / 16
    except IndexError:
        return sum([b.duration for b in track.analysis.segments[-8:]]) / 8

# Initialize cursor
start_point = {"cursor": 0}
	
def managed_transition(track1, track2):
    
    for track in [track1, track2]:
        loudness = track.analysis.loudness
        track.gain = db_2_volume(loudness)

    xfade = float(track1._metadata.track_details['xfade'])
    t1start = first_viable(track1) + float(track1._metadata.track_details['itrim'])
    t1end = last_viable(track1) - float(track1._metadata.track_details['otrim'])
    t1_itrim = float(track2._metadata.track_details['itrim'])
    t1_otrim = float(track1._metadata.track_details['otrim'])
    t1_length = float(track1._metadata.track_details['length'])
    t2_length = float(track2._metadata.track_details['length'])
    t2_otrim = float(track2._metadata.track_details['otrim'])
    t2start = first_viable(track2) + float(track2._metadata.track_details['itrim'])
    t2end = last_viable(track2) - float(track2._metadata.track_details['otrim'])

    if xfade == 0:
        '''Play track1 from cursor point until end of track, less otrim.'''
        pb1 = pb(track1, start_point['cursor'], t1_length - t1_otrim)
        '''Play track2 from start point for 2 seconds less than (length - t2_otrim)'''
        pb2 = pb(track2, t2start, t2_length - t2_otrim - 2)
        '''Set cursor to 2 seconds'''
        start_point['cursor'] = max(t2start + t2_length - t2_otrim - 2, 0)
        log.warning("""No xfade and %r, plus
        %r""",str(pb1), str(pb2))
        return [pb1, pb2]
    else:
        '''offset between start and first theoretical beat.'''
        t2offset = lead_in(track2)
        avg_duration = avg_end_duration(track1)
        playback_end = t1end - (avg_duration * xfade) - t2offset
        playback_duration = playback_end - start_point['cursor']
        mix_duration = t1end - playback_end
        
        pb1 = pb(track1, start_point['cursor'], playback_duration)
        pb2 = cf((track1, track2), (playback_end - .01, t2start), mix_duration - 1)

        log.warning("""
        Complete length of %s (%d) is %r.
        """, track1._metadata.track_details['artist'], track1._metadata.track_details['id'], track1._metadata.track_details['length'])
        
        equal = mix_duration + playback_duration == t1end - start_point['cursor']
        actual = t1end - start_point['cursor']
        desired = mix_duration + playback_duration
        diff = actual - desired
        log.warning("""
        Playback goes from %r to %r for a total duration of %r.
        Mix goes from %r to %r for a total duration of %r.
        Does this all add up? %r.
        We have %r and we want %r.
        We're off by %r.
        Track 2 starts at %r.
        """, start_point['cursor'], playback_end, playback_duration, 
             playback_end, t1end, mix_duration,
             equal, actual, desired, diff, t2start)
        log.warning("Actual mix duration is %r.",pb2.duration)
        start_point['cursor'] = mix_duration -1 + t2start
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