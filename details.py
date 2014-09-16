#!/usr/bin/env python
# encoding: utf=8
"""
details.py

Print track info from pyechonest analysis.

[http://echonest.github.io/pyechonest/track.html]
[https://github.com/echonest/pyechonest/blob/master/pyechonest/artist.py]

By Mike iLL/mZoo.org, 2014-09-16.
"""
from __future__ import print_function
import echonest.remix.audio as audio
import sys, os
import pyechonest.track as track
import pyechonest.artist as artist

usage = """
Usage: 
    python details.py <input_filename>

Example:
    python details.py audio/Track01.mp3 
    python details.py audio/malcolmmarsden.mp3
"""

try:
    input_filename = sys.argv[1]
except:
     print(usage)
     sys.exit(-1)

def artist_details(artist_id):
    star = artist.Artist(artist_id)
    image = star.get_images(results=1)[0]
    print(image)
    bio = star.get_biographies(results=1)[0]
    print(bio)

def main(input_filename):
    """

    """
    audio_object = audio.LocalAudioFile(input_filename, verbose=True, sampleRate = 44100, numChannels = 2)
    id = audio_object.analysis.identifier
    t = track.track_from_id(id)
    
    for attr, value in t.__dict__.iteritems():
        print("{}: {}".format(attr,value))
    try:
        artist_details(t.artist_id)
    except AttributeError:
        print("No Artist Details Found")
    
if __name__ == "__main__":
    main(input_filename)
