//Unprocessed compiled coffeescript
(function() {
  soundManager.setup({
    url: '/static/flash/'
  });

  $(document).ready(function() {
    var getTrackInfo;
    $('body').keyup(function(e) {
      var s;
      s = window.soundManager.sounds.ui360Sound0;
      if (e.keyCode === 32) {
        if (s != null) {
          return s.toggleMute();
        } else {
          return window.threeSixtyPlayer.handleClick({
            target: $('a.sm2_link')[0]
          });
        }
      }
    });
    getTrackInfo = function() {
      return $.getJSON(window.status_url, function(info) {
        var artist, i, id, len, minutes, ref, results, seconds, story, tag, track, track_url;
        tag = 0;
        ref = info.tracks;
        for (i = 0, len = ref.length; i < len; i++) {
          track = ref[i];
          id = track.id;
          console.log(info.ts);
          if (i < info.tracks.length - 3) {
            console.log(`Track #${id} is in the past`);
            continue;
          } else {
            console.log(`Track #${id} is in the future`);
          }
          if (track.details.url) {
            track_url = '';
          } else {
            track_url = '<a href="http://' + track.details.url + '" target="_blank">' + track.details.url + '</a>';
          }
          if (track.details.story) {
            story = track.details.story.replace(/\r?\n|\r+|\r/g, "<br/>");
          } else {
            story = "The story behind this track is still a mystery. Please let us know if you can solve.";
          }
          minutes = Math.floor(track.details.length / 60);
          seconds = Math.floor(track.details.length % 60);
          if (seconds < 10) {
            seconds = "0" + seconds;
          }
          tag += 1;
          artist = document.getElementById('artist' + tag);
          if (artist) {
            artist.innerHTML = track.details.artist;
            document.getElementById('story' + tag).innerHTML = story + '<div class="track_url">' + track_url + '</div>';
            document.getElementById('length' + tag).innerHTML = minutes + ":" + seconds;
          }
        }
        results = [];
        while (1) {
          tag = tag + 1;
          artist = document.getElementById('artist' + tag);
          if (artist) {
            artist.innerHTML = "";
            document.getElementById('length' + tag).innerHTML = "Chunk digging...";
            results.push(document.getElementById('story' + tag).innerHTML = "Still digging around in the chunk selector, dear. Sit tight! :)");
          } else {
            break;
          }
        }
        return results;
      });
    };
    setTimeout(getTrackInfo, 1000);
    return setInterval(getTrackInfo, 30000);
  });

}).call(this);