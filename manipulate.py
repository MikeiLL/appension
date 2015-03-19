#!/usr/bin/python -i
import fore.action as action
from echonest.remix.audio import LocalAudioFile
print("You can load MP3 files with LocalAudioFile()")
print("and manipulate them using the functions in action")
print("To save a modified file: save(f, fn)")
def save(f, fn):
    action.audition_render([f.data], fn)
