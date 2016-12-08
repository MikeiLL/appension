=========
appension
=========

Web player for devil glitch extension
 - Infinite glitch - the longest pop song ever

A few years ago Chris Butler decided to extend The Devil Glitch into infinity. Dozens of artists began writing and recording verses to contribute and re-assembling the gigantic track became rather resource-intensive.

We looked for an internet Music Player with a gapless playback feature, but found none. Chris' friend Henry Lowengard suggested with do something with the Echonest API and it's python companions, PyEchoNest and Remix. I didn't know Python, but was interested in learning and we decided to forge ahead in this direction.

Found my way to Peter Sobot's [Forever.fm](https://github.com/psobot/foreverfm) codebase (or a version of it), forked it and started reading and tinkering. Before long I realized I was way out of my depth and dug up a mentor named [Chris Angelico](https://github.com/Rosuav) with whos help Infinite Glitch was born.

Echonest API has been migrated to a new API that doesn't expose the Track Analysis attributes so we need to replace it. 

## Minimum Viable Product Requirements ##

 * Work with Audio Streams (as opposed to complete files)
 * Insert streaming tracks into output stream randomly
 * Write streams out to a single track
  * Administrate track sequence
  * Return time points and lengths of &ldquo;beats&rdquo; for use in transitions
  * Administrate start and end points at which each transitions to the next

This would probably give us something that _works_, but lacks certain current functionality.

## Additional Current Features ##

 * Crossfade between tracks
 * Combine tracks --- required for the Recording Studio
 * Normalize and Limit track volumes