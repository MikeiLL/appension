** Appension **
=========================================
*Fundamental Design Document*
=========================================

Description
===========

Appension streaming music player for the 
Major Glitch Online Music Project

(Additional elements of website described below.)

Phase One
==================
* Web based UI - web server integration or incorporated HTTP engine
    -Flask
    -Tornado
    
* Responsive HTML/CSS Framework
    -Bootstrap
    
* HTML5 Player
    -Compatible with popular browsers and devices
     
* Directory of (large numbers of) MP3 files

* Music files and selection tied into database
    -Echonest parameters:
        id, title, md5, duration, key, 
        mode, time_signature, 
        danceability, energy, 
        loudness, tempo, fingerprint,
        duration
    -Date added
    -Disable/Enable
    -Lyrics
    -Keywords
    -Description
    -Number of Plays
    -Sort
    -Track Name
    -Artist Bio
    -Artist Image
    -Some details returned by pyechonest.artist and pyechonest.track

* Analyze Audio Files with Pyechonest/Remix
    -Consider a divide and conquer approach to analysis

* Concatenate MP3 files asynchronously
    - trim silence at start and end of track
    
* Stream concatenation to user


Phase Two
==================

* Enable users to direct track assembly:
    -browse
    -sequence
    -filter
        -latest additions
        -preset configurations (favorites, top plays, random)
    
Phase Three
==================    
    
* Concatenated MP3 files will be tied into tempo grid

* Crossfade trailing endings and/or fade-in beginnings

* Display track details to user while playing
    -release_image
    -artist name
    -track ("segment") title
    -date added

===============================
Additional Elements of Website
===============================

* Introduction/Welcome
    -longest pop song ever

* Project Description
    -history

* Contribution/Submission Section
    -process explanation/directions
    -utilities
        -tie in with to http://www.ujam.com
        -details like tempo, key of main piece
    -submission form
    
# List of Participants
	-original
	-subsequent
	-latest
	-high profile
	
* The Music
	-short version: static track
	-full version: static track
	-extended version: dynamic track
	-one minute version: static track
	
* Store
	Tentative
	
* Kudos
	Rolling Stone Review
	
* Latest Additions
    -dynamic stream
    
* Lyrics
    Ultimately from database
    