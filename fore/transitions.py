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

def managed_transition_helper(track1, track2, state, xfade=0, itrim1=0.0, otrim1=0.0, itrim2=0.0, maxlen=None, mode='equal_power', audition_hack=False): 
    """Manage the transition from one track to another

    Most of the parameters should be provided by keyword (in Py3, there'd be * after state).
    state: State mapping - cursor position etc is maintained here
    xfade: Number of tatums/segments to crossfade over
    itrim1: Initial trim of first track - ignored unless starting fresh
    otrim1: Trim end of first track - all these are floating-point seconds
    itrim2: Trim beginning of second track
    maxlen: If set, mix duration will be capped to this (protect against over-long transition)
    mode: Either equal_power or linear
    audition_hack: If set, cursor position will be reduced by the fade length. Yep, it's a hack.
    """
    if "cursor" not in state: state["cursor"] = 0
    for track in (track1, track2):
        loudness = track.analysis.loudness
        track.gain = db_2_volume(loudness)
    # NOTE: All values are floating-point seconds, save xfade which is a number
    # of tatums/segments (assumed to be at average length).
    t1start = first_viable(track1) + itrim1
    t1end = last_viable(track1) - otrim1
    t2start = 0#first_viable(track2) + itrim2
    # offset between start and first theoretical beat.
    t2offset = lead_in(track2)
    if xfade == 0:
        # Ensure that we always crossfade at least a little bit
        fade = 0.0001
        log.info("xfade is zero")
    else:
        # The crossfade is defined based on the tempo at the end
        # of the song, and we fade across X tatums/segments.
        avg_duration = avg_end_duration(track1)
        fade = avg_duration * xfade
    if audition_hack: 
        state['cursor'] -= fade
        log.info("Audition hack")
        log.info(state['cursor'])
    playback_end = t1end - fade - t2offset
    playback_duration = playback_end - state['cursor']
    mix_duration = t1end - playback_end
    log.info(mix_duration)

    if maxlen is not None:
        # Protect from xfade longer than second track.
        while mix_duration > maxlen:
            # Chop half a second at a time (not sure why, but let's maintain it for now)
            mix_duration -= .5
            playback_end += .5
            playback_duration += .5
    pb1 = pb(track1, state['cursor'], playback_duration)
    pb2 = cf((track1, track2), (playback_end - .01, t2start), mix_duration, mode=mode)
    state['cursor'] = mix_duration + t2start
    return [pb1, pb2]

def managed_transition(track1, track2, state):
    """ Manage the transition from track1 to track2
    
    If this is part of a chain of transitions (to track3, track4, ...),
    pass a state dictionary, which should start out empty. Continue to
    pass the same dictionary, and it will be updated to maintain state.
    """
    if state.get("track") != track1._metadata.id:
        # We're not chaining tracks, so wipe out the cursor.
        state["cursor"] = 0
    state["track"] = track2._metadata.id
    return managed_transition_helper(track1, track2, state,
        xfade=int(track1._metadata.track_details['xfade']),
        itrim1=float(track1._metadata.track_details['itrim']),
        otrim1=float(track1._metadata.track_details['otrim']),
        itrim2=float(track2._metadata.track_details['itrim']),
        maxlen=float(track2._metadata.track_details['length']),
    )

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
    # While echonest may return a starting beat part way into the track,
    # we want to assume that beats continue, at a consistent rate, back
    # until the beginning of the track. So our idea of "earliest beat"
    # is actually counting backward by average beat length until we hit
    # the beginning of the track (at time 0.0 or within one beat thereof).
    return earliest_beat % avg_duration
