#!/usr/bin/env python
# encoding: utf=8
from __future__ import print_function

"""
object_anal.py

Use Pympler to Disect Audio Analysis Object returned from Echonest.
Dill module was also useful, but not employed here.

"""
import echonest.remix.audio as audio
import sys, os
from pympler.asizeof import asizeof
from pympler import muppy
from pympler import summary

usage = """
Usage: 
    python object_anal.py <input_filename> 

Example:
    python object_anal.py audio/GlitchBit_BJanoff.mp3 audio/Track01.mp3
"""

try:
    input_filename = sys.argv[1]
except:
     print(usage)
     sys.exit(-1)

def main(input_filename):
    """Create Audio Analysis Object for Profiling purposes.
"""
    audiofile = audio.LocalAudioFile(input_filename)
    
    object_analysis(audiofile)
    get_file_size(input_filename)
    
def object_analysis(obj):
    """Analyze and print resulting information to screen.
"""
    object_size = asizeof(obj)
    print("%s object is %s bytes"% (obj.filename, object_size))
    
    all_objects = muppy.get_objects()
    print("%d objects"%len(all_objects))
    sum1 = summary.summarize(all_objects)
    summary.print_(sum1)

def get_file_size(file):
    """Print size of input file to screen.
"""
    statinfo1 = os.stat(file)
    print("%s filesize is %s"% (file, statinfo1.st_size))
    
if __name__ == "__main__":
    main(input_filename)
