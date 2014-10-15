# Forever.Server #
### Main ###
> `Daemon()` which only does something IF server is called with an argv beyond the script name.
>       potential arguments are `start`, `stop` and `restart`.  
>       If `start` is passed as an argument, subprocess calls server.py is passed to daemon with 'nohup' (written to devnul).  
>       
> Remove logging.root.handlers & replace with custom MultiprocessingHandler.

> Begin logging.

#### *"Starting appname..."* ####

>   Instantiate three queues:

>    1. "track_queue" Queue maxlength 1 - for input to Mixer

#### *"Initializing read queue to hold %2.2f seconds of audio."* ####
    
>    2. "v2" BufferedReadQueue sets a Daemon thread that gets items from a mutliprocessing.Queue
>       and makes them available as a Queue.Queue
>       Max size derived from lame module SAMPLES_PER_FRAME
>       Via Config, which gets values via liveyamlfile module
>           'v2 is sent as member of 1 item list
>    3. "info" 
    
> Send all three queues to mixer module as in, out and info. 

> As mixer, instantiate mixer.Mixer(multiprocessing.Process) with in, out and info queues. 

### Mixer ###
> `mixer.start() -> mixer.run()` (in new process).

>   Iterate through a set of tuples containing an output stream and setting 
>   self.oqueue which is v2_queue and self.setting (default = {}). 

>   Create instance of lame.Lame(threading.Thread), sending oqueue and setting. 

>   Append the instance of Lame() to self.encoders[] list.

>   `lame.start()`

### Lame "Live MP3 streamer." ###

>   Instantiate a subprocess.popen calling the lame encoder, piped to stdin, out, err. 

>   Runs the subprocess from of a new thread. 

>   will 'finish()' and add to `oqueue` when last sample frames have been encoded. 

### Mixer ###

>   Iterate results of `mixer.loop()` generator, which  
    `while` there are **less than 2** tracks  
#### *"Waiting for a new track."* ####
    `get()`s a `track` from the in_queue  
    calls `self.analysis` on it  
    add the result (analysis object) to `self.tracks[]`  
#### *"Got a new track."* ####
#### or *"Track too short! Trying another."* or *"Exception while..."* ####
    grab  `self.tracks[0]`, calculate transition length  
    Send to `capsule_support.initialize`

### Capsule_Support ###

>   `.initialize` returns a `list` containg two items:  
        * fi = Fadein(track, 0, fade_in)  
        * pb = Playback(track, fade_in, inter)  

### Mixer ###

>   * Yield `list[fi, pb]` to `mixer.Run()`.  

>   **Else**  
    Get next two items from `tracks[]`  
    Calculate "stay_time" (between transitions)    
    Send to `capsule_support.make_transition`  
    
### Capsule_Support ###

- - - 
make_transition depends on  

resample_features calls:  

get_central which returns a tuple containing  

* members (segments) btwn end_of_fade_in and start_of_fade_out  
* index of first member  
        
resample_features returns A dictionary including:  

* a numpy matrix of size len(rate) x 12  
* a rate (as assigned by argument or default 'tatums')  
* an index  
        
The `matrix` is an array of arrays,  
One for each audio marker or segment  
(start times realigned based on `get_mean_offset`)  
each containing the 12 floats outlining the 'timbre' shape of the AudioSegment  
(note that [timbre](http://echonest.github.io/remix/apidocs/echonest.remix.audio.AudioSegment-class.html)
is a "twelve-element list with the loudness of each of a principal component of time and/or frequency profile.")  
`make_transition` creates one marker for each of the two tracks  
holding the 'rate' (tatum, beat, etc - assigned) from the track.resampled dictionary  
returned by `resample_features`  
Return a tuple of length 2 containing: 
 
* result of `action.Playback()`  
    which takes track, start and stop and returns  
    portion of track between start and stop  
    possibly volume-equalized using `numpy.multiply`  
    and `cAction.limit`  
* if we can `align` track1, track2, mat1, mat2  
    result of `capsule_support.make_crossmatch` 
    **else**  
    result of `capsule_support.make_crossfade`    
`capsule_support.make_crossmatch` lines tracks up by 'rate'  
using `capsule_support.align`, which takes  
* track1, track2, mat1, mat2  
mat's are `ret.matrix` for each track. 

 
- - -  

>    `capsule_support.align(track1, track2, mat1, mat2)`  

>    get the average segment duration of each track  
>    if logarithm base 2 of marker1 / marker 2 is:  
>     `< -0.5`  
>    `upsample_matrix(matrix2)`  
>    `else if  > 0.5`  
>    `upsample_matrix(matrix1)`  

>    `upsample_matrix` doubles the length of the matrix  
>    duplicating each neighboring row  
>   Basically, if the *magnification* of the rate matrixes are over 50% different,  
>   double the *magnification* for whichever is smaller.

>    rows2 is the number of segments in matrix2  
>    rows1 is the min of num segs in mat1 or num segs in mat2 - min search   
>        OR min markers  

>    Then determine min-loc by getting the lowest value of  
>    linalg.norm() between matrix1 and various slices of matrix 2  


- - -
>    returns *location in mat2*, the *number of rows* used in the *transition*.  
>       and two rates, one of which might be 2 (otherwise 1), the other 1  
>   If rate is 2 it means the matrix of coresponding track was doubled in length.  

>   capsule_support.make_transition  
>   as long as transition is not less than MIN_ALIGN_DURATION  
>   Send `track2, transition and loc` (loc in mat2) to `capsule_support.move_curser`

- - - 
>   `capsule_support.move_curser(track, duration, cursor, buf=MIN_MARKERS)`  
>   * Loop over duration and cursor location  
>   * increase curser (which starts at return from `align`) and dur  
    to point at which either dur is lenth of transition  
    or curser is later than end of matrix minus buffer amount  
    dur is increased by duration of each marker *behind* curser
- - - 
>   returns `duration` and `cursor`.  

>   capsule_support.make_transition  
>   Assign `n` to greater of `loc - cursor` or `MIN_MARKERS`  
>   Send to `make_crossmatch(track1, track2, rate1, rate2, loc, n)`

- - - 
>   capsule_support.make_crossmatch(track1, track2, rate1, rate2, loc, n)  
>   make two `markers` by sending each track's 'rate' (tatum AudioQuantum List) and rate (1 or 2)  
>   to `capsule_support.upsample_list`  
- - -
>   `capsule_support.upsample_list`  
>     if rate is 1 return tatum AudioQuantum List unchanged  
>    if rate is `2`:  
>   double rate of tatums by doubling list and halving times
- - -
>   return `tatum AudioQuantum List` to:  
>   `capsule_support.make_crossmatch`  
>   `start1` is `cursor` (plus `index`) location (x 2 if rate1 = 2)  
>   `start2` is `loc2` (plus `index` (x 2 if rate2 = 2))  
>   Make tuples to send to `action.Crossmatch`  
>   which wants a tuple of two tracks and a tuple of two lists of varying but matching length  
>   `to_tuples` gets the `tatums list`, start and duration and returns a tuple of  
>   `start` and `duration`  
- - -
>   `action.Crossmatch` is an object -> child of `action.Blend`  
>   The dictionary of which looks something like:  
    `{'_Crossmatch__samples': 23722,
 'duration': 0.5379600000000003,  
 'durations': [0.2704399999999999, 0.2675200000000004],  
 'e1': 1.33128,  
 'e2': 6.79377,  
 'l1': [(0.78456, 0.27335999999999994), (1.05792, 0.27336000000000005)],  
 'l2': [(6.26457, 0.2645999999999997), (6.52917, 0.2646000000000006)],  
 's1': 0.78456,  
 's2': 6.26457,  
 't1': <echonest.audio.LocalAudioStream at 0x104b1c750>,  
 't2': <echonest.audio.LocalAudioStream at 0x100420a10>}`  
>   assigned to `xm` within make_transition
- - -
capsule_support.make_transition  
creates an `end_crossmatch` index by adding `n` to `loc` (dividing by rate2)  
if the start of final track2 marker is earlier than the one at  

* `end_crossmatch` plus `inter` plus `transition`  

either reset it to `0` or move it back by the length of `transition`. 
We then send the new `inter`, `end_crossmatch` and `track2` back to `move_cursor`  
to get current duration and move the cursor forward for subsequent operations  
Create a new `start_time` for `Track2` by summing the start time and duration  
for `Track1` as returned from the `Crossmatch` object.  
Instantiate a `Playback(track, start, duration)` object, `pb`  
with `Track2`, `Track2.start_time` and the duration ret. by `move_cursor`.  
return `[xm, pb] to `Mixer`.  

### Mixer ###
`del self.tracks[0].analysis`, `gc.collect()`, and  
yield [xm, pb] to `Run()`
`Run()`  
Else:  
####"Something failed in mixer.run: traceback###  
`Multiprocessing.Process.start()` the mixer.

### Server ###  
If `stream` (module not called with "frontend" flag)    
`hotswap.Hotswap`  

### hotswap.Hotswap(threading.Thread) ###  
Hotswap is used to reload module if it's been updated since last compiled.  
`hotswap.Hotswap(out, mod, gen='generate', *args, **kwargs)`
So we `hotswap.Hotswap(track_queue.put, brain)`  

* `track_queue` is the 1 element multiprocessing.Queue assigned above  
 * `brain` module interfaces with Soundcloud  

### Brain ###  
>   *test brain by running `python -m forever.brain`*  
>   Now hotswap is calling `brain.generate()`  
>   Initialize two lists: `tracks, last` (and "wait" time)  
>   Make an instance of `database.Database()  
>   db = default = 'foreverfm'  
>   (if 'test' in sys.argv run a test)  
>   **ELSE**
>   Loop until `Yield`  
#### "Grabbing fresh tracklist from SoundCloud..." ####  
>   client is a `soundcloud.Client` object  
>   if `tracks` is empty try to get two track sets (limit 200) from `client`  
>   if `client` returns an exception, log warning, `wait` and try again.  
>   Once we have tracks:  
#### "Got %d tracks in %2.2fms." ####  
>   send some details `cube.emit()`  
>   Which prints "events" and times in UDP  
>   to 127.0.0.1, port=1180  
>   along the lines of:  
>   `{"data": {"count": 400, "ms": 220.00399999999988}, "type": "tracks_fetch", "time": "2014-10-10T00:58:20.228560"}`  
>   This data to be sent to a Cube Server (http://square.github.io/cube/)  
>   Cube itself is depreciated. (https://github.com/Marsup/cube or http://hapijs.com as alternative?)
>   Now we check `last` and if it's populated  
>   check if it's final items is in tracks and if it is not  
>   append `last[-1]` to tracks  
>   `brain.cull` track list to remove items matchin blacklist  
>   Send `d`, the database object to `brain.get_force_mix_tracks`  
>   Which tries to get specific SoundCloud track IDs from a text file  
>   returned by `open(config.force_mix_track_list` and  
>   * get from SoundCloud  
>   * add to the database  
>   * yield to `brain.generate`  
>   Add `force_mix_track_list return` to `tracks[]`  
>   Then we try to loop through the `tracks` list again and  
>   `d.merge(self, sc)` each one  
>   Which compares the `soundcloud.id` against items in the database  
>   and returns the `db` values if they exist.  
#### "Solving TSP on %d tracks..." ####
>   reorder `tracks[]` using  
>   `tsp.solve`, which estimates a "best order" for the tracks  
>   (I'm not going to go through the details here.)  
#### "Solved TSP in %2.2fms." ####
>   `emit('tsp_solve', {"count": len(tracks), "ms": t.ms})`  
>   Now for each track in `tracks[]` we  
>   iterate through the list of `criteria` classes:  
>   `criteria = [Tag(), Tempo(), Length(), Spread(), Genre(), Danceability(), Energy(), Loudness()]`  
>   and call the `.postcompute()` method which does nothing except in case `Tag()`  
>   which adds a `'_tags'` attribute to the (soundcloud) track object  
>   populated with a `set()` of the tracks "tags" (or empty set).  
>   Then *if* there's anything in the `last` list  
>   Send `tracks[]` and the `id` of final item in `last[]` to `brain.getIndexOfId`  
>   Which returns the `position` in `tracks[]` of the last item in `last[]`  
>   (or raise a `ValueError`)  
>   Reorder `tracks[]`, starting just above `position` returned by `brain.getIndexOfId`  
>   and adding the rest at the end.  
>   For each track in `tracks[]`  
>   if `brain.get_immediate_tracks` yields an `sc.track` object  
>       based on `config.immediate_track_list`  
>   yield the sc.track object  
>   otherwise yield next track in `tracks[]`  
>   to the `server.queue` set by `Hotswap`    
>   via `server.__name__`  
>   Move remaining `tracks[]` to `last[]` and clear `tracks[]`.  
>   Then via **`server`**,   
>   to `Hotswap` we send `InfoHandler.add, info, 'generate', info_queue, first_frame).start()`  
### server.InfoHandler ###
>   `class InfoHandler(tornado.web.RequestHandler)`  
>   tornado handler for `/all.json` requests  
>   which come from `assets/front.coffee` and deal with visual info  
>   * May examine this later *  
>   to `Hotswap send `monitor.MonitorSocket.update` as output socket  
### monitor.MonitorSocket(tornadio2.conn.SocketConnection) ###
>   * `set()` of monitors  
>   * dict{} of data  
>   `Hotswap` also gets `statistician.generate`  
>   with arguments:  
>   * lambda: StreamHandler.relays,
>   * InfoHandler.stats,
>   * mp3_queue=v2_queue

### statistician.generate(get_relays, get_stats, **queues) ###

>   receives 1. a lambda function that returns  
>   `server.StreamHandler(tornado.web.RequestHandler).relays`  
>   which is a list of relays   
>   as `get_relays` - expected to be callable  
>   `server.StreamHandler` is the tornado handler reached via `/all.mp3`  
>   providing the MP3 stream  
>   2. the `server.InfoHandler.stats` method (as `get_stats`)  
>   returns a `dict{}` containing: `started, samples, duration, width`  
>   3. `mp3_queue=v2_queue` which is the `Queue.Queue`  
>   returned by `bufferedqueue.BufferedReadQueue` (as noted above).  
>   With a pause set by `config.monitor_update_time`,  
>   `statistician.generate` yields a dictionary containing:  

>   * "listeners": a list of http header details for client connectons  
>   * "queues": a list of `queues` and the keys that reference them  
>   * "info": dictionary returned by `server.InfoHandler.stats`  


We then `start()` this `Hotswap` thread.  
>   (Does this mean something is being generated now?) yes.  
>   Now we call a series of tornado.IOLoops:  
>   `tornado.ioloop.PeriodicCallback(callback, callback_time, io_loop=None)`  
>   The callback we send to the first ioLoop is a lambda that uses:  
>   `restart.check` comparing `started_at_timestamp` to modification time of  
>   `restart.txt` and logging errors if necessary.  
>   This function wil run every `config.restart_timeout * 1000` (3000) milliseconds.  
>   Second `tornado.ioLoop` calls `server.InfoHandler.clean` every 5000 milliseconds.  
>   Which looks at `server.InfoHandler.actions[]`, removes *old* items and logs: 
#### "Removing action that ended at %d (now is %d)." ####
>   Then every 10 seconds we call `server.StreamHandler.check`, which does nothing.  
>   We then populate `StreamHandler.relays[]` with:  
>   `listeners.Listeners(v2_queue, "All", first_frame)`  
>   A sub-class of `list`, which gets `queue, name, semaphore`.  
>   and holds a list of tornado streams.  
>   Queue is, of course, our BufferedQueue, "All" the name,  
>   and `server.first_frame` is a `threading.Semaphore(0)` object.  
>   Now we instantiate our `tornado.web.Application`  
>   Handing the routes with:  
>   `tornadio2.TornadioRouter(SocketConnection).apply_routes`  
>   Which takes `connection, user_settings={}, namespace='socket.io', io_loop=None`  
>   `SocketConnection` sub-classes `tornadio2.conn.SocketConnection`  
>   With a dictionary of 2 `__endpoints__`: "info" and "monitor", websockets referencing  
>   `SocketHandler` and `MonitorHandler`.  
>   Into the `application.__dict__` (for tornadio) we also insert:  

>>   * `socket_io_port` which point to `config.socket_port`   
>>   * `enabled_protocols=['websocket', 'xhr-multipart', 'xhr-polling', 'jsonp-polling']`  

>   Instantiate `tornado.ioloop.PeriodicCallback` as `frame_sender`  
>   `PeriodicCallback(StreamHandler.stream_frames, SECONDS_PER_FRAME * 1000)`  
>   `stream_frames` tries to call `listeners.Listener.broadcast` for the listener instance  
>   or logs error: ##### "Could not broadcast due to: \n%s" #####  
### listeners.Listener.broadcast ###
>   **Try**: to (Set `now` to current time and) call `self.__broadcast`  
>>   which gets next item from the (audio / BufferedQueue) `Queue` (non-blocking),  
>>   Increases listener count by one and sets `__starving = False`  
>>   Then Loop through the list of listeners and:  
>>   if `request.connection.stream.closed` try to `finish`  
>>   or try to remove it from the list.  
>>   if it's not closed `write(self.__packet)` (item from audio queue)  
>>   and `flush()` out to network.  

>   If this is the first frame (`not self.__first_frame` init as `False`)  
>   Log:  
#### Sending first frame for All.####
>   Assign `__first_send = time.time()` and release `semaphore`  
>   Subtrack `__first_send` from `now` to get `uptime`  
>   Every 30 streams,  
>   multiply `__count` by 1152 to get total number of (mp3) sample frames in queue  
>   then multiply count by (1152.0 / 44100.0) which gives the  
>   duration of the audio in the queue (based on pcm sample rate).  
>   send some details to `log.txt` and `emit/cube`  
>   Every 2296 frames, log "Sent %d frames over..."  
>   Then we compare to the amount of held time/frames in the `queue`  
>   plus `config.drift_limit` to `uptime`, which is time since queue started  
>   Then as long as the queue is still behind `uptime`  
>   `self.__broadcast()` again  
#### "Queue %s drifting by %2.2f ms. Compensating..." ####

>   **Except**: set `starving=True`  
#### "Dropping frames! Queue %s is starving!" ####
>   `sys.exit(RESTART_EXIT_CODE)`  
>   `frame_sender.start()` the `PeriodicCallback` to `StreamHandler.stream_frames`  
>   which broadcasts all the listener relays.  
>   Listen to the instance of `tornado.web.Application`

### Lame ###

>   Acquire via `threading.Semaphore()`
        
        