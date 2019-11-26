=========
appension
=========

Web player for devil glitch extension
 - Infinite glitch - the longest pop song ever
 
## Requirements ##

Postgresql database server (on OSX `brew install postgresql`)
FFMPEG audio manipulation and rendering (on OSX `brew install ffmpeg`)

## Installation ##
  * Create a virtualenv `python3 -m venv glitch`
  * * `cd glitch`
  * * `source bin/activate`
  	
  * Install pip Requirements `pip install -r requirements.txt`
  
  * Create an `apikeys.py` file based on `apikeys_sample.py`
  
  * Generate a `privkey.pem` file in the main directory, above "glitch"
  * * `ssh-keygen -f ~/path/to/id_rsa.pub -m 'PEM' -e > privkey.pem`
  
  * Insure postgres is running (on OSX) `brew services start postgresql`
  * * Usually the package  manager creates a database for you, but if you get an error that database <user> does not exist, try running the command `createdb` ([reference](https://stackoverflow.com/a/17936043/2223106))
  
  * Create the database tables `python -m glitch tables --confirm`
  * * (You can test by running this command without the `--confirm` flag.)
  
  * Create a new user
  * * `python3 -m glitch create-user name email password`
  
  * Make new user admin
  * * ``psql `whoami` ``
  * * `update users set status=1 where id = 1;`
  * * `update users set user_level=2 where id = 1;`
  
  * Create an audio directory `mkdir audio` and put some mp3 files in it.
  
  * Add files to glitchery `python3 -m glitch importmp3 audio/*.mp3`
  
  * Visit the address chosen in `apikeys` for `admin_address` to make tracks active (or do via psql).
  
 
## Start Server ##
python3 -m glitch main
 
## Start Renderer ##
python3 -m glitch renderer

## Build/Rebuild Major Glitch ##
python3 -m glitch major-glitch

## For dev if you want to play tracks more quietly ##
python3 -m glitch renderer --gain=-10 (where -10 is a number of decibels)

## To View All CMDLINE Commands ##
python -m glitch --help

## On Unix system with Systemd ##
Use bash to run the makeservice.sh file, then start both services with command:
sudo systemctl start glitch glitch-renderer

## If using a service with Unicorn and using the Pike Monitor ##
sudo systemctl start glitch.service

check status:
systemctl status glitch

run monitor like this:
sudo pike outage.pike
OR (chmod +x outage.pike)
sudo ./outage.pike

## SSL Certificates are generated via Let's Enctypt

[See this link](https://certbot.eff.org/lets-encrypt/debianjessie-other)
Also create a deploy hook for renewal:
```
/etc/letsencrypt/renewal-hooks/deploy/appension 
cp /etc/letsencrypt/live/infiniteglitch.net/fullchain.pem /etc/letsencrypt/live/infiniteglitch.net/privkey.pem /home/mikekilmer/appension

```

## To manually renew certificate with certbot:
```
sudo certbot renew --webroot -w /home/mikekilmer/appension
( --dry-run --debug-challenges flags can be useful )
```

## On a Fresh Server ##

In order to have services start automatically on reboot via systemd, each service must be symlinked thusly:

sudo systemctl enable glitch glitch-renderer glitch-redirect
sudo systemctl start glitch glitch-renderer glitch-redirect

## Environment ##

Running on Debian 10, Buster with Python 3.7.3 

Requirements versions as of 31 July 2019

 * aiohttp         3.5.4      
 * amen            0.0.3      
 * asn1crypto      0.24.0     
 * async-timeout   3.0.1      
 * attrs           19.1.0     
 * audioread       2.1.8      
 * certifi         2019.6.16  
 * cffi            1.12.3     
 * chardet         3.0.4      
 * Click           7.0        
 * clize           4.0.3      
 * cryptography    2.7        
 * DateTime        4.3        
 * decorator       4.4.0      
 * docutils        0.15.2     
 * Flask           1.1.1      
 * Flask-Login     0.4.1      
 * gunicorn        19.9.0     
 * idna            2.8        
 * itsdangerous    1.1.0      
 * Jinja2          2.10.1     
 * joblib          0.13.2     
 * librosa         0.7.0      
 * llvmlite        0.29.0     
 * MarkupSafe      1.1.1      
 * multidict       4.5.2      
 * mutagen         1.42.0     
 * numba           0.45.0     
 * numpy           1.17.0     
 * od              1.0        
 * pandas          0.25.0     
 * pip             18.1       
 * pkg-resources   0.0.0      
 * psycopg2-binary 2.8.3      
 * pycparser       2.19       
 * pycrypto        2.6.1      
 * pydub           0.23.1     
 * pyOpenSSL       19.0.0     
 * PySoundFile     0.9.0.post1
 * python-dateutil 2.8.0      
 * pytz            2019.1     
 * requests        2.22.0     
 * resampy         0.2.1      
 * scikit-learn    0.21.3     
 * scipy           1.3.0      
 * setuptools      40.8.0     
 * sigtools        2.0.2      
 * simplejson      3.16.0     
 * six             1.12.0     
 * SoundFile       0.10.2     
 * stop-words      2018.7.23  
 * urllib3         1.25.3     
 * Werkzeug        0.15.5     
 * yarl            1.3.0      
 * zope.interface  4.6.0 

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