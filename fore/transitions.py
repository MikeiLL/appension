#!/usr/bin/env python
# encoding: utf=8

"""
transitions.py

Create transitions between tracks. Used by Mixer and Audition.

Created by Mike iLL/mZoo with Rosuav oversight and input
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

def managed_transition(track1, track2, state=None):
    """ Manage the transition from track1 to track2
    
    If this is part of a chain of transitions (to track3, track4, ...),
    pass a state dictionary, which should start out empty. Continue to
    pass the same dictionary, and it will be updated to maintain state.
    """
    if state is None:
        # No state object passed, so no state retention;
        # we'll be discarding this when we're done.
        state = {}
    if "cursor" not in state:
        # Initialize new state mapping to save us having to use .get() everywhere
        state["cursor"] = state["track"] = 0
    if state["track"] != track1._metadata.id:
        # We're not chaining tracks, so wipe out the cursor.
        state["cursor"] = 0
    state["track"] = track2._metadata.id
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
    '''offset between start and first theoretical beat.'''
    t2offset = lead_in(track2)
    if xfade == 0:
        quick_fade = float(1)
        # We want the playback to last until a fraction of a second before
        # last viable segment, as contained in t2offset
        playback_end = t1end - quick_fade - t2offset
        playback_duration = playback_end - state['cursor'] - quick_fade
        mix_duration = t1end - playback_end + quick_fade
    else:
        avg_duration = avg_end_duration(track1)
        playback_end = t1end - (avg_duration * xfade) - t2offset
        playback_duration = playback_end - state['cursor']
        mix_duration = t1end - playback_end
    '''Protect from xfade longer than second track.'''
    while t2_length - mix_duration <= 0:
        mix_duration -= .5
        playback_end += .5
        playback_duration += .5
        
    
    pb1 = pb(track1, state['cursor'], playback_duration)
    pb2 = cf((track1, track2), (playback_end - .01, t2start), mix_duration, mode='equal_power') #other mode option: 'linear'

    equal = mix_duration + playback_duration == t1end - state['cursor']
    actual = t1end - state['cursor']
    desired = mix_duration + playback_duration
    diff = actual - desired
    
    state['cursor'] = mix_duration + t2start
    return [pb1, pb2]

def lead_in(track):
    """
    Return the time between start of track and first beat.
    """
    try:
        avg_duration = sum([b.duration for b in track.analysis.beats[:8]]) / 8
        earliest_beat = track.analysis.beats[0].start
    except IndexError:
        log.warning("No beats returned for track by %r.", track._metadata.track_details['artist'])
        return track.analysis.segments[0].start
    while earliest_beat >= 0 + avg_duration:
        earliest_beat -= avg_duration
    offset = earliest_beat
    return offset