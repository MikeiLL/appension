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

		function UrlExists(url) {
			console.log(url)
			jQuery.noConflict();
				jQuery( document ).ready(function( $ ) {
					(url).load(function() {
					return true;
					}).bind('error', function() {
						return false;
					});
				});
			}

	function probe(url) {
		console.log("Probing "+url+"...");
		var xhr = new XMLHttpRequest();
		xhr.open("HEAD", url);
		xhr.onreadystatechange = function() {
			if (xhr.readyState != 4) return;
			if (xhr.status == 404) {
				setTimeout(probe, 1000, url);
				log.innerHTML += " .";
			} else {
				var au2 = document.createElement('audio');
				au2.controls = true;
				au2.src = url;
				var li = document.createElement('li');
				li.appendChild(au2);
				document.getElementById("demo_player").appendChild(li);
				document.getElementById('loading').style.display = "none";
			}
		};
		xhr.send();
	}
      			
	function uploadAudio(mp3Data){
	  	document.getElementById('record_controls').style.display = "none";
		log.innerHTML += "\n" + "Uploading track... ";
		var reader = new FileReader();
		reader.onload = function(event){
			var fd = new FormData();
			var username = document.getElementById('username').innerHTML;
			file_username = username.replace(/ /g,"_");
			var mp3Name = encodeURIComponent(file_username + '_' + new Date().getTime() + '.mp3');
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
				log.innerHTML += "\n" + "File uploaded, analyzing...";
	  			document.getElementById('audition_player').style.display = "block";
				probe('audition_audio/'+mp3Name);
				displaySubmissionForm(mp3Name);
			});
		};      
		reader.readAsDataURL(mp3Data);
	}
	
		function displaySubmissionForm(mp3Name){
			var submission_form=document.createElement('FORM');
			submission_form.name='submissionForm';
			submission_form.method='POST';
			submission_form.action='/submit';
			var title = document.createElement("INPUT");
			
			title.type = "text";
			//title.className = "css-class-name";
			button.type='SUBMIT';
			button.value='Submit Track';
			var button = document.createElement("BUTTON");
			button.type='SUBMIT';
			button.value='Submit Track';
            		button.innerHTML='Submit Track';
			button.onclick=displaySubmissionForm;
			var mp3_file_data=document.createElement('INPUT');
			mp3_file_data.type='HIDDEN';
			mp3_file_data.name='mp3Name';
			mp3_file_data.value=mp3Name;
			submission_form.appendChild(mp3_file_data);
			submission_form.appendChild(button);
			document.getElementById('submit_buttons').style.display = "block";
			document.getElementById('submit_buttons').appendChild(submission_form);
			
			}

		function displaySubmissionForm(mp3Name){
			alert(mp3Name);
			}
	
  window.Recorder = Recorder;


})(window);

		
