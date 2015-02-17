#!/usr/bin/env python
# encoding: utf=8

"""
audition.py

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

log = logging.getLogger(__name__)

LOUDNESS_THRESH = -8

def audition(files, xfade=0, otrim=0, itrim=0, user_name="transition"):
    filenames = ['audio/' + filename.encode("UTF-8") for filename in files]
    two_tracks = make_LAFs(filenames)
    transition = managed_transition(two_tracks[1], two_tracks[2], xfade=xfade, otrim=otrim, itrim=itrim)
    log.warning("What we have here is a list and it looks like %r and %r", filenames[0], filenames[1])
    audition_render(transition, 'transition_audio/transition.mp3')

def make_LAFs(files):
    """

    """
    q = file_queue(files)
    localaudiofiles = {}
    number = 1
    while not q.empty():
        file = q.get()
        localaudiofiles[number] = LocalAudioStream(file)
        number += 1
        
    return localaudiofiles
        
def file_queue(files):
    """
    Get list of files, add them to a queue and return the queue.
    """
    q = Queue() 
    
    for f in files:
        q.put(f)
    
    return q

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

    if xfade == 0:
        '''Play track1 from cursor point until end of track, less otrim.'''
        pb1 = pb(track1, start_point['cursor'], t1_length - t1_otrim)
        '''Play track2 from start point for 2 seconds less than (length - t2_otrim)'''
        pb2 = pb(track2, t2start, t2_length - t2_otrim - 2)
        '''Set cursor to 2 seconds'''
        start_point['cursor'] = max(t2start + t2_length - t2_otrim - 2, 0)
        return [pb1, pb2]
    else:
        '''offset between start and first theoretical beat.'''
        t2offset = 0 #lead_in(track2)
        avg_duration = avg_end_duration(track1)
        start = track.analysis.duration - (10 + (avg_duration * xfade))
        playback_end = t1end - (avg_duration * xfade) - t2offset
        playback_duration = playback_end - start_point['cursor']
        mix_duration = t1end - playback_end
    
        pb1 = pb(track1, start, playback_duration)
        pb2 = cf((track1, track2), (playback_end - .01, t2start), mix_duration, mode=mode) 
        pb3 = pb(track2, t2start + mix_duration, 10)
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