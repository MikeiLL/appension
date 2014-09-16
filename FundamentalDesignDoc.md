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
    * Tornado
    
* Responsive HTML/CSS Framework
    * Bootstrap
    
* HTML5 Player
    * Compatible with popular browsers and devices
    * _Are Standard controls (pause, forward, back) feasible_?
     
* Directory of (large numbers of) MP3 files

* Music files and selection tied into database
    * Echonest.Remix parameters:
    
            `id, title, md5, duration, key,   
            mode, time_signature,  
            danceability, energy,  
            loudness, tempo, fingerprint,  
            duration  `
        
    * Date added
    * Disable/Enable
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


## Phase Two


* Enable users to direct track assembly:
    * browse
    * sequence
    * filter
        * latest additions
        * preset configurations (favorites, top plays, random)
    
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