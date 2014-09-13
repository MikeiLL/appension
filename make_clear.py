#!/usr/bin/env python
# encoding: utf=8
from __future__ import print_function

"""
make_clear.py

Create two LocalAudioFile objects, append to AudioQuantumList, then delete them and render
The idea is to be able to create AudioFile objects, save them, then clear the memory.

Created by Mike iLL / mZoo.org
"""

usage = """
Usage: 
    python make_clear.py <directory> <output file>

Example:
    python make_clear.py audio "make_me.mp3"
    python -m memory_profiler make_clear.py audio "make_me.mp3" - using memory_profiler
"""
import os, sys, gc, time
import echonest.remix.audio as audio
import dill

# @profile # uncomment to use memory_profiler
def do_work(directory, outfile):
    "Call each function in order"
    x = audio.AudioQuantumList() 
    for f in file_list(directory):
        audiofile = make_objects(f)
        x = add_to_list(audiofile, x)
        audiofile = clear_memory(audiofile)
    #x.render().encode(outfile) # uncomment to actually render file
            
def file_list(directory):
    "Make a list of all mp3 files in specified directory."
    aud = []
    files = os.listdir(directory)
    for f in files:
        # collect the files
        if f.rsplit('.', 1)[1].lower() == 'mp3':
            filename = os.path.join(directory, f)
            aud.append(filename)
    return aud
                
def make_objects(file):
    "Create audio_object from audio file"
    audiofile = audio.LocalAudioFile(file)
    return audiofile

def add_to_list(file, list): 
    "Add both files to the list"  
    list.append(file)
    return list
    
def clear_memory(file1):
    """Save the file into pickle.load-able format?
    Can we override audioobject with none?
    And render the file even after AufioFileObjects have been deleted?"""
    file1.save()
    return None

if __name__ == '__main__':
    try:
        outfile = sys.argv[-1]
        directory = sys.argv[-2]
    except:
        print(usage)
        sys.exit(-1)
    do_work(directory, outfile)
    
"""
To reimport audioObjects use:
with open('audio/Track01.mp3.analysis.en') as f:
    audiofile = pickle.load(f)
    
with open('audio/Track02.mp3.analysis.en') as f:
    audiofile = dill.load(f)
"""