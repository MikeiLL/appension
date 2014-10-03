#Server#
    ##Main##
        Daemon() which only does something IF server is called with an argv beyond the script name
                potential arguments are start, stop and restart. 
                If start is passed, subprocess calls module with 'nohup' - written to devnul
        Remove logging.root.handlers & replace with custom MultiprocessingHandler
        Begin logging
        Instantiate three queues:
            -"track_read" Queue maxlength 1 - for input to Mixer
            -"v2" BufferedReadQueue sets a Daemon thread that gets items from a mtlprocessing.Queue
                    and makes them available as a Queue.Queue
                    Max size derived from lame module SAMPLES_PER_FRAME
                    Via Config, which gets values via liveyamlfile module
                    'v2 is sent as member of 1 item list
            -"info" 
        Send all three queues to mixer module as in, out and info.
        
        As mixer, instantiate mixer.Mixer(multiprocessing.Process) with in, out and info queues
        
        ##mixer.start() -> mixer.run()##
        Iterate through a set of tuples containing an output stream and setting 
            self.oqueue which is v2_queue and self.setting (default = {})
            create instance of lame.Lame(threading.Thread), sending oqueue and setting
        
        Append the instance of Lame() to self.encoders[] list
        lame.start()
        
        ##Lame "Live MP3 streamer."##
        Instantiates a subprocess.popen calling the lame encoder, piped to stdin, out, err
        Runs the subprocess inside of a new thread
        will finish() when last sample frames have been encoded and adds to opqueue