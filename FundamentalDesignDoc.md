# Appension 

- - - - - - - - - - - - - - - - -
## Fundamental Design Document

## Description

### Appension streaming music player for the   
### Major Glitch Online Music Project

(_Additional elements of website described below_.)

## Phase One

* Web based UI * web server integration or incorporated HTTP engine
    * Flask
    * Tornado ?
    
* Responsive HTML/CSS Framework
    * Bootstrap/Boilerplate
    
* HTML5 Player
    * Compatible with popular browsers and devices ?
    * _Are Standard controls (pause, forward, back) feasible_?
     

* Music files and selection tied into database
    * PostgreSQL
        * Blob of MP3 Data
        * Reference ID (sequential integer - surrogate key)
        * File name in above directory, or BLOB of actual MP3 data
        * Echonest.Remix parameters:
    
                `id, title, md5, duration, key,   
                mode, time_signature,  
                danceability, energy,  
                loudness, tempo, fingerprint,  
                duration`
        
        * Date added
        * Disabled/Enabled flag
        * Visibility status? (eg have newly-uploaded tracks visible only to admins until curated)
        * Lyrics
        * Keywords
        * Description
        * Number of Plays
        * Sort Order
        * Track Name
        * Artist Bio
        * Artist Image
        * _Some of the above returned by [pyechonest.artist][p.artist] and [pyechonest.track][p.track]_

* Analyze Audio Files with Pyechonest/Remix
    * Consider a divide and conquer approach to analysis

* Concatenate MP3 files asynchronously
    * trim silence at start and end of track
    
* Stream concatenation to user
    * Jukebox mode or per-user streaming?
        * Jukebox - when a new user connects, s/he hears whatever's currently playing
	* Per-user - a stream is created for each user, starting from the beginning, and may be randomized in order
    * Advantages of jukebox:
        * Possible savings on encoding/decoding work. Do the work once and send to everyone.
        * Roughly O(1) RAM and CPU usage, but with a high constant factor.
    * Advantages of per-user:
        * Simplicity. Write the code so it works for a single connected user, then it'll be fine for everyone.
        * Roughly O(n) RAM/CPU usage, with minimal constant factor; there'd be a maximum concurrent users based on hardware, rather than having a high cost regardless of who's using it.
        * Guaranteed well-formed streams - no need to finesse the beginning of a connected client.
        * Straight-forward restart/reload procedure: new clients get the new code. Follow Minstrel Hall/Gypsum model, if possible.

* Administrative Backend
    * multiple admin accounts
    * maintain page content
    * view and edit track info in DB
    
* Testing Framework
    * Does code function as expected?
    * Are we within memory/CPU limits of server?

## Phase Two

* Enable users to direct track assembly:
    * browse
    * sequence
    * filter
        * latest additions
        * preset configurations (favorites, top plays, random)
        
* Administrative Backend
    * edit playback features (track sequence, filters)

    
## Phase Three

    
* Concatenated MP3 files will be tied into tempo grid

* Crossfade trailing endings and/or fade*in beginnings

* Display track details to user while playing
    * __release_image__
    * __artist name__
    * __track ("segment") title__
    * __date added__

- - - - - - - - - - - - - - - - -

## Additional Elements of Website


* Introduction/Welcome
    * longest pop song ever

* Project Description
    * history

* Contribution/Submission Section
    * process explanation/directions
    * utilities
        * tie in with to [uJam](www.ujam.com)
        * details like tempo, key of [Devil Glitch](www.devilglitch.net)
    * submission form
    
* List of Participants
	* original
	* subsequent
	* latest
	* high profile
	
* The Music
	* short version: static track
	* full version: static track
	* extended version: dynamic track
	* one minute version: static track
	
* Store
	* _Tentative_
	
* Kudos
	* Rolling Stone Review
	
* Latest Additions
    * dynamic stream
    
* Lyrics
    * Ultimately from database
    >Currently single text file.
    
 
 [p.artist]: https://github.com/echonest/pyechonest/blob/master/pyechonest/artist.py
 [p.track]: http://echonest.github.io/pyechonest/track.html