#!/usr/bin/env python
# encoding: utf=8
from __future__ import print_function

"""
append.py

Accepts songs on the commandline, order them, optionally abridge, and output an audio file

(Abridge is used to make checking transitions easier - cuts out most of middle of track)

Created by Mike iLL / mZoo.org
Based on Capsule by Tristan Jehan and Jason Sundram.
"""

usage = """
Usage: 
    python append.py <input_filename> <output_filename>

Example:
    
    python append.py -v -e -a -n "long1" audio/Track01.mp3 audio/Track02.mp3 audio/GlitchBit_BJanoff.mp3
    
    NOTE: GlitchBit_BJanoff.mp3 tracks returns very little analysis data!
          malcolmmarsden.mp3 also "interesting"
    
"""
import os
import sys
from optparse import OptionParser
from echonest.remix.action import make_stereo
from echonest.remix.audio import LocalAudioFile
from pyechonest import util
from append_support import equalize_tracks, appension, abridge, pre_post, display_actions, trim_silence
from action import render
from pympler.asizeof import asizeof


def tuples(l, n=2):
    """ returns n-tuples from l.
        e.g. tuples(range(4), n=2) -> [(0, 1), (1, 2), (2, 3)]
    """
    return zip(*[l[i:] for i in range(n)])


def do_work(audio_files, options):

    inter = float(options.inter)
    trans = float(options.transition)
    order = bool(options.order)
    equal = bool(options.equalize)
    verbose = bool(options.verbose)
    abridged = bool(options.abridged)
    
    analyze = lambda x : LocalAudioFile(x, verbose=verbose, sampleRate = 44100, numChannels = 2)
    
    def analize(x):
        return LocalAudioFile(x, verbose=verbose, sampleRate = 44100, numChannels = 2)
        
    tracks = map(analize, audio_files)
    for tr in tracks:
    	track_length = len(tr)

    # decide on an initial order for those tracks
    if order == True:
        if verbose: print("Ordering tracks...")
        tracks = order_tracks(tracks)
    
    if equal == True:
        equalize_tracks(tracks)
        if verbose:

            print()
            for track in tracks:
                print("Vol = %.0f%%\t%s" % (track.gain*100.0, track.filename))
            print()
            
    if abridged == True:
        abridge(tracks)
     
    trim_silence(tracks)
        
    # compute resampled and normalized matrices
    for track in tracks: 
        track = make_stereo(track)
            
    if len(tracks) < 1: return []
    # Initial transition. Should contain 2 instructions: fadein, and playback.
    #if verbose: print("Computing transitions...")
    #start = initialize(tracks[0], inter, trans)
    
    # Middle transitions. Should each contain 2 instructions: crossmatch, playback.
    middle = []

    print("%d duplicates"%len([i for i, x in enumerate(middle) if middle.count(x) > 1]))
    [middle.extend(appension(t)) for t in tracks]
    print("%d duplicates"%len([i for i, x in enumerate(middle) if middle.count(x) > 1]))
    # Last chunk. Should contain 1 instruction: fadeout.
    #end = terminate(tracks[-1], FADE_OUT)
    
    return middle

def get_options(warn=False):
    usage = "usage: %s [options] <list of mp3s>" % sys.argv[0]
    parser = OptionParser(usage=usage)
    parser.add_option("-t", "--transition", default=1, help="transition (in seconds) default=8")
    parser.add_option("-i", "--inter", default=8, help="section that's not transitioning (in seconds) default=8")
    parser.add_option("-o", "--order", action="store_true", help="automatically order tracks")
    parser.add_option("-e", "--equalize", action="store_true", help="automatically adjust volumes")
    parser.add_option("-v", "--verbose", action="store_true", help="show results on screen")                      
    parser.add_option("-a", "--abridged", action="store_true", help="cut out center of track (for testing)")           
    parser.add_option("-n", "--mix_name", default=8888777766665, help="name this mix")      
    parser.add_option("-p", "--pdb", default=True, help="dummy; here for not crashing when using nose")
    
    (options, args) = parser.parse_args()
    if warn and len(args) < 2: 
        parser.print_help()
    return (options, args)
    
def main():
    options, args = get_options(warn=True);
    for a in args:

        print("track = %s"%a)

    actions = do_work(args, options)
    verbose = bool(options.verbose)
    
    if verbose:
        display_actions(actions)
        print("Output Duration = %.3f sec" % sum(act.duration for act in actions))
    
        print("Rendering...")
    # Send to renderer
    mixname = str(options.mix_name)
    final_file = mixname + ".mp3"
    print(final_file)
    render(actions, final_file, verbose)
    return 1
    
if __name__ == "__main__":
    main()
    # for profiling, do this:
    #import cProfile
    #cProfile.run('main()', 'capsule_prof')
    # then in ipython:
    #import pstats
    #p = pstats.Stats('capsule_prof')
    #p.sort_stats('cumulative').print_stats(30)
