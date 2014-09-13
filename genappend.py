#!/usr/bin/env python
# encoding: utf=8
from __future__ import print_function

"""
genappend.py

Using Queue and Generators to work with Saved Remix Objects.

"""

usage = """
Usage: 
    python genappend.py 

Example:
    
    python genappend.py 
    
"""

# System modules
from Queue import Queue
from threading import Thread
import time
import glob
import echonest.remix.audio as audio
import pickle

q = Queue()    

files = glob.glob('audio/*.en')

for f in files:
    q.put(f)
    
def lazarus(filename):
    with open(filename) as f:
        return pickle.load(f)

def forever(q):
    t1 = q.get()
    q.task_done()
    while not q.empty():
        t2 = q.get()
        q.task_done()
        audiofile1 = lazarus(t1)
        audiofile2 = lazarus(t2)
        yield (audiofile1, audiofile2)
        t1 = t2
        
def show_transitions():
    while not q.empty():
        while True:
            try:
                next_two = here.next()
                print(next_two[0].filename, '->', next_two[1].filename)
            except StopIteration:
                print("All done.")
                return

if __name__ == "__main__":
    here = forever(q)
    show_transitions()
          
