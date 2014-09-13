#!/usr/bin/env python
# encoding: utf=8
"""
pieces.py

Analyze with Echonest, print out details about track and potentially render various pieces.

[http://developer.echonest.com/docs/v4/_static/AnalyzeDocumentation.pdf]

tatums
: list of tatum markers, in seconds. Tatums represent the lowest regular pulse train that a listener intuitively
infers from the timing of perceived musical events (segments).
‣
beats
: list of beat markers, in seconds. A beat is the basic time unit of a piece of music; for example, each tick of
a metronome. Beats are typically multiples of tatums.
‣
bars
: list of bar markers, in seconds. A bar (or measure) is a segment of time defined as a given number of beats.
Bar offsets also indicate downbeats, the first beat of the measure.
‣
sections
: a set of section markers, in seconds. Sections are defined by large variations in rhythm or timbre, e.g.
chorus, verse, bridge, guitar solo, etc. Each section contains its own descriptions of tempo, key, mode,
time_signature, and loudness.

By Mike iLL/mZoo.org, 2014-07-20.
"""
from __future__ import print_function
import echonest.remix.audio as audio
import sys, os


usage = """
Usage: 
    python pieces.py <input_filename> <output_filename>

Example:
    python pieces.py audio/Track01.mp3 Abridged.mp3
    python pieces.py audio/GlitchBit_BJanoff.mp3 Abridged.mp3
"""

try:
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
except:
     print(usage)
     sys.exit(-1)

spacer = "*" + (' ' * 58) + "*"
border = "*" * 60     

def track_details(track):
    """
    Print echonest analysis details of track to stdout. 
    """
    segments = track.segments
    
    sections = track.sections
    heading = "  Some details about " + input_filename + "  "
    print(heading.center(60,"*"), spacer)
    print("Track Duration: {0:14.4f}".format(track.duration))
    
    if track.beats:
        beats = track.beats
        bars = track.bars
        tatums = track.tatums
        columns = "*Element***Tatums***Beats***Bars***Segments"
        counts = "* Count {0:6d} {1:9d} {2:8d} {3:7d} ".format(len(tatums), len(beats), len(bars), len(segments))
        starting = "* Start: {0:5f} {1:9f} {2:8f} {3:7f} ".format(tatums[0].start, beats[0].start, 
                                                                    beats[0].start, segments[0].start)
        ending = "* End: {0:5.4f} {1:9.4f} {2:8.4f} {3:7.4f} ".format(tatums[-1].end, beats[-1].end, 
                                                                    beats[-1].end, segments[-1].end)
        first_seg_loudness_header = " First Segment Loudness ".center(len(columns), '*')
        first_seg_loudness_cols = "****StartVol**** MaxVol == -60 ****Confidence***".center(len(columns), '*')
        first_seg_loudness = "{0:10.4f}, {1:12} {2:18s}".format(segments[0].loudness_begin, 
                                                                segments[0].loudness_max == -60, 
                                                                segments[0].confidence)
        print(columns, os.linesep, spacer, os.linesep, counts, 
            os.linesep, starting, os.linesep, ending, os.linesep, spacer, os.linesep, spacer)
        print(first_seg_loudness_header, os.linesep, first_seg_loudness_cols, 
            os.linesep, first_seg_loudness, os.linesep, spacer)
    else:
        no_beats = "********No Beats Detected********"
        print(no_beats)
        print(spacer)
        if not len(track.segments) == None:
            print("*  Found {} segments".format(len(track.segments)))
            
        print("*" * len(no_beats))
        
    print(spacer)

def pre_tatum(track):
    """
    Return segment items that begin before the first tatum 
    """
    start = audio.AudioQuantumList()
    segs_in = 0
    for segment in track.segments:
        if (segment.loudness_max > -60) and (segment.tatum == None)\
        and (segment.start < track.tatums[0].start):
            start.append(segment)
            segs_in += 1
    print("*", segs_in, "viable pre-tatum segment(s).")
    return {"music": start, "segment count": segs_in}
        
def pre_bar(track):
    """
    Return tatum items that begin before the first bar 
    """
    tatums_in=0
    lead_in = audio.AudioQuantumList()
    for tatum in track.tatums:
        if tatum.start < track.bars[0].start:
            tatums_in += 1
            lead_in.append(tatum)
    print("*", tatums_in, "tatum lead in.")
    return {"music": lead_in, "tatum count": tatums_in}
    
def first_bars(track):
    """
    Return the first 4 bars.
    """
    start_bars = track.bars[:4]
    first_bars = audio.AudioQuantumList()
    for bar in start_bars:
        first_bars.append(bar)
    return first_bars
    
def last_bars(track):
    """
    Return the last four bars. 
    """
    end_bars = track.bars[-4:]
    last_bars = audio.AudioQuantumList()
    for bar in end_bars:
        last_bars.append(bar)
    return last_bars

def post_bar(track):
    """
    Return tatum items that end after final bar, begin before
    final segment start and are not equal to segment start 
    """
    tatums_out=0
    lead_out = audio.AudioQuantumList() 
    for tatum in track.tatums:
        if tatum.end > track.bars[-1].end and tatum.start < track.segments[-1].start \
        and not tatum == track.segments[-1].tatum:
            tatums_out += 1
            lead_out.append(tatum)
    try:
        print("*   {d} tatum outro.").format(tatums_out)
    except AttributeError:
        print("No outro tatums.")
    return {"music": lead_out, "tatum count": tatums_out}
    
def post_tatum(track):
    """
    Return segment items that extent beyond final tatum end.
    """
    try:
        print("Final Segment: {}").format(track.segments[-1])
    except AttributeError:
        print("No segments extend past final tatum.")
    try:    
        print("Final Tatum: {}").format(track.tatums[-1])
    except AttributeError:
        print("Unable to return final tatum")
    end = audio.AudioQuantumList()
    segs_out = 0
    for segment in track.segments:
        if (segment.loudness_max > -60) and (segment.start >= track.tatums[-1].start):
            end.append(segment)
            segs_out += 1
    try:
        print("*   {d} post-tatum segment(s).").format(segs_out)
    except AttributeError:
        print("No post-tatum segment(s).")
    return {"music": end, "segment count": segs_out}
    
def trim_silence(track):
    """
    Filter AudioQuantumList() by loudness_max to trim silence
    """
    result = audio.AudioQuantumList()
    for segment in track.segments:
        if segment.loudness_max > -60:
            result.append(segment)
    return {"music": result}
    
def first_bits(units, num=4):
    """
    Return only the first num units
    """
    result = audio.AudioQuantumList()
    count = 0
    for unit in units[:num]:
    	if count < num:
    		print(count)
    		result.append(units[count])
    		count += 1
    return result
    
def last_bits(units, num=4):
    """
    Return only the last num units
    """
    result = audio.AudioQuantumList()
    count = len(units)
    num = count - num
    print(num, count)
    for unit in units[num:]:
        if num < count:
            result.append(units[num])
            num += 1
    return result

def main(input_filename, output_filename):
    """
    Call functions which print tracks details and return portions of track.
    """
    audiofile = audio.LocalAudioFile(input_filename)
    track = audiofile.analysis
    track_details(track)
    
    if track.beats and track.tatums:
        print(spacer)
        start = pre_tatum(track)
        print(spacer)
        leadin = pre_bar(track)
        print(spacer)
        first = first_bars(track)
        print(spacer)
        last = last_bars(track)
        print(spacer)
        post = post_bar(track)
        print(spacer)
        tail = post_tatum(track)
        print(spacer)
        final = {"music": start["music"]+leadin["music"]+first+last+post["music"]+tail["music"]}
        test = {"music": tail["music"]}
    else:
        final = {"music": trim_silence(track)["music"]}
        print(spacer)
    
    print(spacer, os.linesep, border)
    
    """Below we can replace track with some other dictionary
    Containing elements from above (start, leadin, first, etc)
    So as to be able to audition what is returned.
    """
    out = audio.getpieces(audiofile, final["music"])
    out.encode(output_filename)

if __name__ == "__main__":
    main(input_filename, output_filename)
