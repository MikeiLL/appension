=======
appension
=========

Echonest player for devil glitch extension
 - major glitch - the longest pop song ever

This is a collection of scripts for exploring ways to dynamically append segments of a VERY LONG song.

Currently, append.py rather loosely appends the tracks together, based on the echonest Capsule library.

The kernels.py echonest script demonsrates the adding the defer=true keyword to LocalAudioFile, 
for which the actual audio is not loaded until actually used.

Currently exploring methods of lazy-loading, divide and conquer, threading, streaming etc 
so that the large amounts of data can be handled.

Some details about getting echonest remix running on your server 
can be found at: 

http://www.mzoo.org/getting-the-python-echonest-remix-package-running/
http://echonest.github.io/remix/python.html

basically you add to your .bash_profile:
# Adding EchoNest Key to environment
export ECHO_NEST_API_KEY="the_key_they_sent_you"

=======
# Welcome to Echo Nest Remix

Echo Nest Remix is **the Internet Synthesizer.** 
Make amazing things from music, automatically.  Turn any music or video into Python, Flash, or Javascript code.  

Want more cowbell? [Remix can do it.](http://www.morecowbell.dj/ "")  
Want to make it swing? [Remix can do it.](http://swingify.cloudapp.net/ "")  
Want to turn any track into drum & bass? [Remix can do it.](http://the.wubmachine.com/ "")  
Want to make new music videos out of old ones? [Remix can do it.](http://www.youtube.com/watch?v=_bW7AkhgQpc/ "")  

## Getting Started
We've made a shiny new page for getting Remix installed: <http://echonest.github.com/remix/> - if you have any problems, let us know!

-![alt text](http://i.imgur.com/WWLYo.gif "Frustrated cat can't believe this is the 12th time he's clicked on an auto-linked README.md URL")
