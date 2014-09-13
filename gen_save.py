#!/usr/bin/env python
# encoding: utf=8
from __future__ import print_function
"""
gen_save.py

Using Queue and Generators to Save Remix Objects so we don't have to use API every time.

"""

usage = """
Usage: 
    python gen_save.py 

Example:
    
    python gen_save.py 
    
"""

# System modules
from Queue import Queue
from threading import Thread
import time
import glob
import echonest.remix.audio as audio
import pickle

q = Queue()    

def save_me(filename):
    audiofile = audio.LocalAudioFile(filename)
    audiofile.save()
    
def make_and_save():
    files = glob.glob('audio/*.mp3')
        
    for f in files:
        q.put(f)

    while not q.empty():
        file = q.get()
        save_me(file)

if __name__ == "__main__":
    make_and_save()
          
