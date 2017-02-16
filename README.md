=========
appension
=========

Web player for devil glitch extension
 - Infinite glitch - the longest pop song ever
 
## Start Server ##
python3 -m glitch main
 
## Start Renderer ##
python3 -m glitch renderer

## OR: On Unix system with Systemd ##
Use bash to run the makeservice.sh file, then start both services with command:
sudo systemctl start glitch glitch-renderer

## To View All CMDLINE Commands ##
python -m glitch --help

## For dev if you want to play tracks more quietly ##
python3 -m glitch renderer gain=-10 (where -10 is a number of decibels)

# A brief History #
A few years ago Chris Butler decided to extend The Devil Glitch into infinity. Dozens of artists began writing and recording verses to contribute and re-assembling the gigantic track became rather resource-intensive.

We looked for an internet Music Player with a gapless playback feature, but found none. Chris' friend Henry Lowengard suggested with do something with the Echonest API and it's python companions, PyEchoNest and Remix. I didn't know Python, but was interested in learning and we decided to forge ahead in this direction.

Found my way to Peter Sobot's [Forever.fm](https://github.com/psobot/foreverfm) codebase (or a version of it), forked it and started reading and tinkering. Before long I realized I was way out of my depth and dug up a mentor named [Chris Angelico](https://github.com/Rosuav) with whos help Infinite Glitch was born.

Echonest API has been migrated to a new API that doesn't expose the Track Analysis attributes so we need to replace it. 

## Minimum Viable Product Requirements ##

 * Work with Audio Streams (as opposed to complete files)
 * Insert streaming tracks --- gap-lessly --- into output stream randomly
 * Write streams out to a single track
 ### Admin ###
  * Sequence of tracks for Single Rendered File
  * Trim start time either in milliseconds or &ldquo;beats&rdquo; for use in transitions

This would probably give us something that _works_, but lacks certain current functionality.

## Additional Current Features ##

 * Crossfade between tracks
 * Combine tracks --- required for the Recording Studio
 * Normalize and Limit track volumes
 
## What can [Amen](https://github.com/algorithmic-music-exploration/amen) do? ##
 
The Amen echo_nest_converter AudioAnalysis object contains a reference to the original file as well as list of analysis data:
 
 * sections
 * bars
 * beats
 * tatums
 * segments
  
It looks like `sections`, `tatums` and `segments` may not yet be implemented. As far as I can tell the amen.synthesize function is what renders an final audio file, but as we're dealing with streams we may need to handle differently. Possibly RealAudioStream from Forever.fm will work, or maybe some variation on a Threading object.

For combining the two elements in the Recording Studio, the [PyDub](https://github.com/jiaaro/pydub) might be perfect. It [doesn't support streaming](https://github.com/jiaaro/pydub/issues/124) so not sure if we could use it to crossfade streaming PMC or any other type of audio data very easily.