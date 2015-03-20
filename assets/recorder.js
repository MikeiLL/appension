(function(window) {

  var recordWavWorker = new Worker('static/uncompiledjs/recorderWorker.js');
  var encoderMp3Worker = new Worker('static/uncompiledjs/mp3Worker.js');
  
  
  var Recorder = function(source) {

    var bufferLen = 4096;
    var recording = false;

    this.context = source.context;
    

    /*
      ScriptProcessorNode createScriptProcessor (optional unsigned long bufferSize = 0,
       optional unsigned long numberOfInputChannels = 2, optional unsigned long numberOfOutputChannels = 2 );
    */

    this.node = (this.context.createScriptProcessor || this.context.createJavaScriptNode).call(this.context, bufferLen, 1, 1);
    this.node.connect(this.context.destination); //this should not be necessary

    this.node.onaudioprocess = function(e) {

      if (!recording)
        return;

      var channelLeft = e.inputBuffer.getChannelData(0);

      console.log('onAudioProcess' + channelLeft.length);

      encoderMp3Worker.postMessage({
        command: 'encode',
        buf: channelLeft
      });

      recordWavWorker.postMessage({
        command: 'record',
        buffer: channelLeft
      });

    }

    source.connect(this.node);

    this.record = function() {

      if (recording)
        return false;

      recording = true;

      var sampleRate = this.context.sampleRate;
/*
      console.log("Initializing WAV");
      log.innerHTML += "\n" + "Creating Empty WAV";

      recordWavWorker.postMessage({
        command: 'init',
        config: {
          sampleRate: sampleRate
        }
      });*/

      console.log("Initializing to Mp3");
      log.innerHTML += "\n" + "Creating Empty Mp3:" + sampleRate;

      encoderMp3Worker.postMessage({
        command: 'init',
        config: {
          channels: 1,
          mode: 3 /* means MONO*/ ,
          samplerate: 22050,
          bitrate: 64,
          insamplerate: sampleRate
        }
      });

    }

    this.stop = function() {

      if (!recording)
        return;
/*
      recordWavWorker.postMessage({
        command: 'finish'
      });
*/
      encoderMp3Worker.postMessage({
        command: 'finish'
      });

      recording = false;

    }

    encoderMp3Worker.onmessage = function(e) {

      var command = e.data.command;
      console.log('encoderMp3Worker - onmessage: ' + command);

      switch (command) {
        case 'data':
          var buf = e.data.buf;
          console.log('Receiving data from mp3-Encoder');

          //maybe you want to send to websocket channel, as:
          //https://github.com/akrennmair/speech-to-server

          break;
          
        case 'mp3':
          var buf = e.data.buf;
    	  	endFile(buf, 'mp3');
          // Removed the terminate of the worker - terminate does not allow multiple recordings
          encoderMp3Worker.terminate();
          //encoderMp3Worker = null;
          break;
      }

    };
/*
    recordWavWorker.onmessage = function(e) {

      var command = e.data.command;

      console.log('recordWavWorker - onmessage: ' + command);

      switch (command) {
        case 'wav':
          endFile(e.data.buf, 'wav');
          break;
      }

    };
    */

    function endFile(blob, extension) {

      console.log("Done converting to " + extension);
      
      log.innerHTML += "\n" + "Done converting to " + extension;

      console.log("the blob " + blob + " " + blob.size + " " + blob.type);

      var url = URL.createObjectURL(blob);
      var li = document.createElement('li');
      var hf = document.createElement('a');
      hf.href = url;
      hf.download = new Date().toISOString() + '.' + extension;
      hf.innerHTML = hf.download;
      //li.appendChild(hf);

      var au = document.createElement('audio');
      au.controls = true;
      au.src = url;
      au2 = document.getElementById('BackgroundTrack');
      li.appendChild(au);

      // Upload file to server - uncomment below
	  document.getElementById('upload_button').style.display = "inline";
      
	  document.getElementById("upload").onclick = function(){
      	uploadAudio(blob);
      }
      
      document.getElementById("reset").onclick = function(){
  		window.location.reload(false);
      }
      

      recordingslist.appendChild(li);

    }

  };

	
	function uploadAudio(mp3Data){
	  	document.getElementById('record_controls').style.display = "none";
		var reader = new FileReader();
		reader.onload = function(event){
			var fd = new FormData();
			var username = document.getElementById('username').innerHTML;
			file_username = username.replace(/ /g,"_");
      		console.log(username, file_username)
			var mp3Name = encodeURIComponent(file_username + '_' + new Date().getTime() + '.mp3');
			console.log("mp3name = " + mp3Name);
			fd.append('fname', mp3Name);
			fd.append('username', username);
			fd.append('data', event.target.result);
			jQuery.ajax({
				type: 'POST',
				url: 'recorder',
				data: fd,
				processData: false,
				contentType: false
			}).done(function(data) {
				console.log("File uploaded");
      			log.innerHTML += "\n" + "File uploaded";
      			var li = document.createElement('li');
	  			document.getElementById('audition_player').style.display = "block";
				var au2 = document.createElement('audio');
				au2.controls = true;
				au2.src = 'audition_audio/'+mp3Name;
      			li.appendChild(au2);
      			demo_player.appendChild(li);
			});
		};      
		reader.readAsDataURL(mp3Data);
	}
	
  window.Recorder = Recorder;

})(window);
