#!/usr/bin/env python
# encoding: utf=8

"""
audition.py

Used to create a transition between two files for admin to reference in setting crossfade and trim between 
Track1 and Track2 in sequential series.

Created by Mike iLL with mentorship of Rosuav.
"""
from __future__ import print_function
import echonest.remix.audio as audio
from mixer import LocalAudioStream
import echonest.remix.audio as audio
import logging
from action import Crossfade as cf
from action import Playback as pb
from action import render, audition_render
from Queue import Queue
import os
import time

log = logging.getLogger(__name__)

LOUDNESS_THRESH = -8

def audition(files, xfade=0, otrim=0, itrim=0, dest="transition.mp3"):
    filenames = ['audio/' + filename.encode("UTF-8") for filename in files]
    tracks = [LocalAudioStream(file) for file in filenames]
    transition = managed_transition(tracks[0], tracks[1], xfade=xfade, otrim=otrim, itrim=itrim)
    audition_render(transition, 'transition_audio/'+dest)
    # Once we're done rendering, and still on a background thread,
    # clean out the transition_audio directory of files that are more
    # than a week old. We could use st_atime instead of st_mtime, but
    # not all file systems reliably record atimes, and the chances
    # that someone is actively using a transition file for a week are
    # sufficiently low that we can say "don't do that then".
    now = time.time()
    for fn in os.listdir("transition_audio"):
        if now-os.stat("transition_audio/"+fn).st_mtime > 604800:
            os.remove("transition_audio/"+fn)

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

def managed_transition(track1, track2, xfade = 0, otrim = 0, itrim = 0, mode = 'equal_power'): 
    """Return three renderable Echonest objects. 

    (other mode option is 'linear')
    """
    for track in [track1, track2]:
        loudness = track.analysis.loudness
        track.gain = db_2_volume(loudness)

    xfade = float(xfade)
    t1start = first_viable(track1) + float(itrim)
    t1end = last_viable(track1) - float(otrim)
    t1_itrim = float(itrim)
    t1_otrim = float(otrim)
    t1_length = float(track1.analysis.duration)
    t2_length = float(track2.analysis.duration)
    t2_otrim = float(otrim)
    t2start = first_viable(track2) + float(itrim)
    t2end = last_viable(track2) - float(otrim)
    '''offset between start and first theoretical beat.'''
    t2offset = lead_in(track2)
    if xfade == 0:
        quick_fade = float(0.01)
        # Start this many seconds from the end
        start = track1.analysis.duration - (4 + quick_fade)
        playback_end = t1end - quick_fade - t2offset
        playback_duration = playback_end - start - quick_fade
        mix_duration = t1end - playback_end + quick_fade
        
    else:
        avg_duration = avg_end_duration(track1)
        start = track1.analysis.duration - (6 + (avg_duration * xfade))
        playback_end = t1end - (avg_duration * xfade) - t2offset
        playback_duration = playback_end - start
        mix_duration = t1end - playback_end
    '''Protect from xfade longer than second track.'''
    while t2_length - mix_duration <= 0:
        mix_duration -= .5
        playback_end += .5
        playback_duration += .5
    pb1 = pb(track1, start, playback_duration)
    pb2 = cf((track1, track2), (playback_end - .01, t2start), mix_duration, mode=mode) 
    pb3 = pb(track2, t2start + mix_duration, 6)
    return [pb1, pb2, pb3]
        
def lead_in(track):
    """
    Return the time between start of track and first beat.
    """
    try:
        avg_duration = sum([b.duration for b in track.analysis.beats[:8]]) / 8
        earliest_beat = track.analysis.beats[0].start
    except IndexError:
        log.warning("No beats returned for track.")
        earliest_beat = track.analysis.segments[0].start
    while earliest_beat >= 0 + avg_duration:
        earliest_beat -= avg_duration
    offset = earliest_beat
    return offset