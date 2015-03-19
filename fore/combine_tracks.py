#!/usr/bin/env python
# encoding: utf=8

"""
audition.py

Functions to combine 'Basic' and 'Overdub' tracks from 'Glitch Recording Studio'.

Created by Mike iLL with mentorship of Rosuav.

track1 = audio.LocalAudioFile('acapella/Mike_iLL_a_capella.mp3')
track2 = audio.LocalAudioFile('instrumentals/dgacousticlikMP3.mp3')
"""
from __future__ import print_function
import echonest.remix.audio as audio
import echonest.remix.audio as audio
import logging
from action import Playback as pb
from action import Fadeout as fo
from action import render, audition_render, remove_channel, left_right_merge

log = logging.getLogger(__name__)

LOUDNESS_THRESH = -8

def combine_tracks(track1, track2, remove=0):
    if remove == 'left':
        track2 = remove_channel(track2)
    elif remove == 'right':
        track2 = remove_channel(track2, remove="right")
    return left_right_merge(track1, track2)
    
	
def format_track(track, itrim=0, otrim=0, fadeout=5):
	playback = pb(track, itrim, track.analysis.duration - otrim)
	#fadeout = fo(track, track.analysis.duration - otrim, fadeout)
	return [playback]
	
def render_track(file1, file2, itrim=0, fadeout=5, remove=0):
    filename = file1
    track1 = audio.LocalAudioFile('acapella/'+file1)
    track2 = audio.LocalAudioFile('instrumentals/'+file2)
    otrim = max(track1.analysis.duration, track2.analysis.duration) - min(track1.analysis.duration, track2.analysis.duration)
    together = combine_tracks(track1, track2, remove=remove)
    formatted = format_track(together, itrim=itrim, otrim=otrim, fadeout=fadeout)
    render(formatted, 'audition_audio/'+filename)