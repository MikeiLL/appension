# Forever.Server #
### Main ###
> `Daemon()` which only does something IF server is called with an argv beyond the script name.
>       potential arguments are `start`, `stop` and `restart`.  
>       If `start` is passed, subprocess calls server.py is passed to daemon with 'nohup' (written to devnul).  
>        * Can you read from that somewhere?
>       
> Remove logging.root.handlers & replace with custom MultiprocessingHandler.

> Begin logging.

#### *"Starting appname..."* ####

>   Instantiate three queues:

>    1. "track_read" Queue maxlength 1 - for input to Mixer

#### *"Initializing read queue to hold %2.2f seconds of audio."* ####
    
>    2. "v2" BufferedReadQueue sets a Daemon thread that gets items from a mtlprocessing.Queue
>       and makes them available as a Queue.Queue
>       Max size derived from lame module SAMPLES_PER_FRAME
>       Via Config, which gets values via liveyamlfile module
>           'v2 is sent as member of 1 item list
>    3. "info" 
    
> Send all three queues to mixer module as in, out and info. 

> As mixer, instantiate mixer.Mixer(multiprocessing.Process) with in, out and info queues. 

### Mixer ###
> `mixer.start() -> mixer.run()`.

>   Iterate through a set of tuples containing an output stream and setting 
>   self.oqueue which is v2_queue and self.setting (default = {}). 

>   Create instance of lame.Lame(threading.Thread), sending oqueue and setting. 

>   Append the instance of Lame() to self.encoders[] list.

>   `lame.start()`

### Lame "Live MP3 streamer." ###

>   Instantiate a subprocess.popen calling the lame encoder, piped to stdin, out, err. 

>   Runs the subprocess inside of a new thread. 

>   will 'finish()' and add to `opqueue` when last sample frames have been encoded. 

### Mixer ###

>   Iterate results of `mixer.loop()` generator, which  
    `while` there are **less than 2** tracks  
#### *"Waiting for a new track."* ####
    `get()`s a `track` from the in_queue  
    calls `self.analysis` on it  
    add the result (analysis object) to `self.tracks[]`  
#### *"Got a new track."* ####
    grab  `self.tracks[0]`, calculate transition length  
    Send to `capsule_support.initialize`

### Capsule_Support ###

>   `.initialize` returns a list containg two items:  
        * fi = Fadein(track, 0, fade_in)  
        * pb = Playback(track, fade_in, inter)  

### Mixer ###

>   * Yield to `Run()`.  

>   **Else**  
    Get next two items from `tracks[]`  
    Calculate "stay_time" (between transitions)    
    Send to `capsule_support.make_transition`  
    
### Capsule_Support ###

>   make_transition depends on  

>   resample_features calls:  

>   get_central which returns a tuple containing  

        * members (segments) btwn end_of_fade_in and start_of_fade_out  
        * index of first member  
        
>   resample_features returns A dictionary including:  
        * a numpy matrix of size len(rate) x 12  
        * a rate (as assigned by argument or default 'tatums')  
        * an index  
>   The `matrix` is an array of arrays,  
>   One for each audio marker or segment  
>   (start times realigned based on `get_mean_offset`)  
>   each containing the 12 floats outlining the 'timbre' shape of the AudioSegment  
>   `make_transition` creates one marker for each of the two tracks  
>   holding the 'rate' (tatum, beat, etc - assigned) from the track.resampled dictionary  
>   returned by `resample_features`  
>   Return a tuple of length 2 containing:  
>   * result of `action.Playback()`  
>       which takes track, start and stop and returns  
>       portion of track between start and stop  
>       possibly volume-equalized using `numpy.multiply`  
>       and `cAction.limit`  
>   * if we can `align` track1, track2, mat1, mat2  
>       result of `capsule_support.make_crossmatch` 
>       **else**  
>       result of `capsule_support.make_crossfade`    
>   `capsule_support.make_crossmatch` lines tracks up by 'rate'  
>   using `capsule_support.align`, which takes  
>   * track1, track2, mat1, mat2  
>   mat's are `ret.matrix` for each track. 
 
- - -  

>    `align`  

>    get the average segment duration of each track  
>    if logarithm base 2 of marker1 / marker 2 is:  
>     `< -0.5`  
>    `upsample_matrix(matrix2)`  
>    `else if  > 0.5`  
>    `upsample_matrix(matrix1)`  

>    `upsample_matrix` doubles the length of the matrix  
>    duplicating each neighboring row  

>    rows2 is the number of segments in matrix2  
>    rows1 is the min of num segs in mat1 or num segs in mat2 - min search   
>        OR min markers  

>    Then determine min-loc by getting the lowest value of  
>    linalg.norm() between matrix1 and various slices of matrix 2  


- - -
>    returns location in mat2 and the number of rows used in the transition.  
>       and two rates, one of which might be two (otherwise 1), the other 1

### Mixer ###

>   yield to `Run()`

### Lame ###

>   Acquire via `threading.Semaphore()`
        
        