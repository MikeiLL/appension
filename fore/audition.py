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
from action import audition_render
from Queue import Queue
import os
import time
from .transitions import managed_transition_helper

log = logging.getLogger(__name__)

LOUDNESS_THRESH = -8

def audition(files, xfade=0, otrim=0.0, itrim=0.0, dest="transition.mp3"):
    """
    Render transition audition files and delete them after a week.
    """
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

def managed_transition(track1, track2, xfade=0, otrim=0.0, itrim=0.0):
	state = {"cursor": track1.analysis.duration - 6.0 - float(otrim)}
	ret = managed_transition_helper(track1, track2, state,
		xfade=int(xfade),
		otrim1=float(otrim),
		itrim2=float(itrim),
		maxlen=float(track2.analysis.duration),
		audition_hack=True,
	)
	ret.append(pb(track2, state['cursor'], 6))
	print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
	print(ret)
	return ret
