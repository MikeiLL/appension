#!/usr/bin/python -i
import fore.action as action
from echonest.remix.audio import LocalAudioFile
from fore.mixer import LocalAudioStream as las
print("You can load MP3 files with LocalAudioFile() or las()")
print("and manipulate them using the functions in action")
print("To save a modified file: save(f, fn)")
def save(f, fn):
    action.audition_render([f.data], fn)
    

