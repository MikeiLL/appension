(function() {
  (function() {
    var lastTime, vendors, x;
    lastTime = 0;
    vendors = ["ms", "moz", "webkit", "o"];
    x = 0;
    while (x < vendors.length && !window.requestAnimationFrame) {
      window.requestAnimationFrame = window[vendors[x] + "RequestAnimationFrame"];
      window.cancelAnimationFrame = window[vendors[x] + "CancelAnimationFrame"] || window[vendors[x] + "CancelRequestAnimationFrame"];
      ++x;
    }
    if (!window.requestAnimationFrame) {
      window.requestAnimationFrame = function(callback, element) {
        var currTime, id, timeToCall;
        currTime = new Date().getTime();
        timeToCall = Math.max(0, 16 - (currTime - lastTime));
        id = window.setTimeout(function() {
          return callback(currTime + timeToCall);
        }, timeToCall);
        lastTime = currTime + timeToCall;
        return id;
      };
    }
    if (!window.cancelAnimationFrame) {
      return window.cancelAnimationFrame = function(id) {
        return clearTimeout(id);
      };
    }
  })();

}).call(this);

(function() {
  var BUFFERED, DONE_TRACKS_LIMIT, Frame, MAGIC_REGEX, MIN_LISTENERS, NUM_TRACKS, OFFSET, TIMING_INTERVAL, Titular, Waveform, comma, connectedly, format_uptime, getPersistent,
    __indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; };

  window.log = function() {
    log.history = log.history || [];
    log.history.push(arguments);
    if (this.console) {
      return console.log(Array.prototype.slice.call(arguments));
    }
  };

  soundManager.setup({
    url: '/static/flash/'
  });

  TIMING_INTERVAL = 30000;

  NUM_TRACKS = 5;

  OFFSET = 5;

  BUFFERED = OFFSET;

  MIN_LISTENERS = 30;

  DONE_TRACKS_LIMIT = 8;

  MAGIC_REGEX = /(\s*-*\s*((\[|\(|\*|~)[^\)\]]*(mp3|dl|description|free|download|comment|out now|clip|bonus|preview|teaser|in store|follow me|follow on|prod|full|snip|exclusive|beatport|original mix)+[^\)\]]*(\]|\)|\*|~)|((OUT NOW( ON \w*)?|free|download|preview|follow me|follow on|teaser|in store|mp3|dl|description|full|snip|exclusive|beatport|original mix).*$))\s*|\[(.*?)\])/i;

  comma = function(x) {
    if (x != null) {
      return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    } else {
      return x;
    }
  };

  window.ping = 0;

  window.serverTime = function() {
    return (+(new Date)) - window.ping;
  };

  Frame = (function() {
    function Frame(init, is_new) {
      var k, v;
      for (k in init) {
        v = init[k];
        this[k] = v;
      }
      this.image = null;
      this.div = null;
      this.id = "track_" + this.tracks[0].metadata.id;
      this["new"] = is_new ? 'new' : '';
      while (document.getElementById(this.id)) {
        this.id += "_";
      }
      this.parseMetaData();
    }

    Frame.prototype.parseMetaData = function() {
      var matches, other, _, _artist, _title;
      matches = this.tracks[0].metadata.title.match(/(.*?) by (.*)/i);
      if (matches != null) {
        _ = matches[0], this.title = matches[1], this.artist = matches[2];
        matches = this.artist.match(/(.*?)\s+-\s+(.*)/i);
        if (matches != null) {
          _ = matches[0], this.artist = matches[1], other = matches[2];
        }
      } else {
        matches = this.tracks[0].metadata.title.match(/(.*?)\s*-\s+(.*)/i);
        if (matches != null) {
          _ = matches[0], this.artist = matches[1], this.title = matches[2];
        } else {
          this.title = this.tracks[0].metadata.title;
          this.artist = this.tracks[0].metadata.user.username;
        }
      }
      matches = this.title.match(/([^\[\]]*?)( - ([^\[\]\(\)]*)|(\[.*\]))/i);
      if (matches != null) {
        _ = matches[0], this.title = matches[1], _ = matches[2], other = matches[3];
      }
      _title = this.title.replace(MAGIC_REGEX, "");
      if (_title.length > 0) {
        this.title = _title;
      }
      _artist = this.artist.replace(MAGIC_REGEX, "");
      if (_artist.length > 0) {
        this.artist = _artist;
      }
      if (this.title[0] === '"' && this.title[this.title.length - 1] === '"') {
        this.title = this.title.slice(1, this.title.length - 1).trim();
      }
      this.img = this.tracks[0].metadata.artwork_url != null ? this.tracks[0].metadata.artwork_url : this.tracks[0].metadata.user.avatar_url;
      this.playcount = comma(this.tracks[0].metadata.playback_count);
      this.downloads = comma(this.tracks[0].metadata.download_count);
      this.favoritings = comma(this.tracks[0].metadata.favoritings_count);
      this.stats = (this.playcount != null) && (this.downloads != null) && this.favoritings;
      this.buttons = true;
      this.nid = this.tracks[0].metadata.id;
      this.download = this.tracks[0].metadata.download_url;
      this.purchaselink = this.tracks[0].metadata.purchase_url;
      this.purchasetext = this.tracks[0].metadata.purchase_title;
      if (this.purchasetext == null) {
        this.purchasetext = "Buy";
      }
      return this.url = this.tracks[0].metadata.permalink_url;
    };

    Frame.prototype.twitter = function() {
      var text;
      text = "Check out this track: " + this.url + " " + (this.playing() ? "playing now" : "I found") + " on";
      return "http://twitter.com/share?text=" + (encodeURIComponent(text));
    };

    Frame.prototype.html = function(first) {
      var _new, _ref, _ref1;
      if (first == null) {
        first = false;
      }
      _new = this["new"];
      this["new"] = '';
      return "<div class='track " + _new + " " + (this.played() && !first ? "hidden" : "") + "' id='" + this.id + "' target=\"_blank\" href=\"" + this.url + "\">\n  <a class=\"coverart\" href=\"" + this.url + "\" target=\"_blank\"><img src=\"" + this.img + "\" /></a>\n  <div class=\"text\">\n    <a class=\"title\" href=\"" + this.url + "\" target=\"_blank\">" + this.title + "</a>\n    <span class=\"artist\">" + this.artist + "</span>\n  </div>\n  <div class='buttons'>\n    " + (this.id ? "<a href='#' title='Like \"" + this.title + "\" on SoundCloud.' data-track='" + this.nid + "' class='like " + ((SC.favorites != null) && (_ref = this.nid, __indexOf.call(SC.favorites, _ref) >= 0) ? "selected" : "") + "'>&nbsp;</a> <a href='#' title='Tweet about \"" + this.title + "\".' target='_blank' class='share'>&nbsp;</a>" : "") + "\n    " + (this.download ? "<a href='" + this.download + "' title='Download \"" + this.title + "\" from SoundCloud.'  class='download " + ((SC.downloaded != null) && (_ref1 = this.nid, __indexOf.call(SC.downloaded, _ref1) >= 0) ? "selected" : "") + "' data-track='" + this.nid + "'>&nbsp;</a>" : "") + "\n    " + (this.url ? "<a href='" + this.url + "' title='View \"" + this.title + "\" on SoundCloud.' target='_blank' class='sc'>&nbsp;</a><a title='Make \"" + this.title + "\" your new jam.' href='http://www.thisismyjam.com/jam/create?url=" + (encodeURIComponent(this.url)) + "' target='_blank' class='jam'>&nbsp;</a>" : "") + "\n    " + (this.purchaselink && this.purchasetext ? "<a href='" + this.purchaselink + "' target='_blank' class='buy'>" + this.purchasetext + "</a>" : "") + "\n  </div>\n  " + (this.stats ? "<div class='stats'> " + ((this.playcount != null) && this.playcount !== '0' ? "<span class='count playback'>" + this.playcount + "</span>" : "") + " " + ((this.downloads != null) && this.downloads !== '0' ? "<span class='count download'>" + this.downloads + "</span>" : "") + " " + ((this.favoritings != null) && this.favoritings !== '0' ? "<span class='count favoritings'>" + this.favoritings + "</span>" : "") + " </div>" : "") + "\n</div>";
    };

    Frame.prototype.played = function() {
      return (this.time + this.duration + BUFFERED) < (window.serverTime() / 1000);
    };

    Frame.prototype.playing = function() {
      return ((this.time + BUFFERED) < (window.serverTime() / 1000)) && !this.played();
    };

    Frame.prototype.intendedParent = function() {
      return document.getElementById(this.played() ? "done" : "tracks");
    };

    Frame.prototype.render = function() {
      var id, parent;
      if (this.action !== "Playback") {
        return;
      }
      if (this.div != null) {
        return this.relayout();
      }
      parent = this.intendedParent();
      $(parent).prepend(this.html(true));
      id = this.id;
      setTimeout((function() {
        return $("#" + id).removeClass('new hidden');
      }), 100);
      return this.div = document.getElementById(this.id);
    };

    Frame.prototype.relayout = function() {
      var div, html, neighbour, newparent;
      if (this.div.parentNode == null) {
        this.div = document.getElementById(this.id);
      }
      newparent = document.getElementById(this.played() ? "done" : "tracks");
      if (this.div.parentNode !== newparent) {
        neighbour = this.div.parentNode.children[this.div.parentNode.children.length - 2];
        $(this.div).addClass("ending");
        $(neighbour).addClass("next");
        div = this.div;
        html = this.html();
        return setTimeout(function() {
          $(neighbour).removeClass("next");
          div.parentNode.removeChild(div);
          newparent.innerHTML = html + newparent.innerHTML;
          return setTimeout(function() {
            var end;
            $(".hidden", newparent).removeClass('hidden');
            if (newparent.children.length > DONE_TRACKS_LIMIT) {
              end = newparent.children[newparent.children.length - 1];
              $(end).addClass('hidden');
              return setTimeout(function() {
                return newparent.removeChild(end);
              }, 1000);
            }
          }, 100);
        }, 1400);
      }
    };

    return Frame;

  })();

  Waveform = (function() {
    Waveform.prototype.speed = 5;

    function Waveform(canvas) {
      this.canvas = canvas;
      this.delay = 0;
      this._offset = $("#menu").outerWidth();
      this.frames = [];
      this.context = this.canvas.getContext("2d");
      this.overlap = navigator.userAgent.match(/chrome/i) != null ? 0 : 1;
      this.layout();
      this.drawloop();
    }

    Waveform.prototype.offset = function() {
      return this._offset + this.buffered();
    };

    Waveform.prototype.buffered = function() {
      return (window.threeSixtyPlayer.bufferDelay * this.speed / 1000.0) + OFFSET;
    };

    Waveform.prototype.layout = function() {
      return this.canvas.width = window.innerWidth;
    };

    Waveform.prototype.drawloop = function() {
      var me;
      this.draw();
      me = this;
      if (this.stop != null) {
        return;
      }
      return setTimeout((function() {
        return me.drawloop();
      }), 100);
    };

    Waveform.prototype.draw = function() {
      var frame, i, left, nowtime, right, _i, _j, _len, _ref, _ref1;
      BUFFERED = this.buffered();
      if ((window.soundManager.sounds.ui360Sound0 != null) && window.soundManager.sounds.ui360Sound0.paused) {
        if (this.paused_at == null) {
          this.paused_at = window.serverTime();
        }
        return;
      } else if (this.paused_at != null) {
        this.delay += window.serverTime() - this.paused_at;
        delete this.paused_at;
      }
      if (this.frames[0] != null) {
        this.context.clearRect(0, 0, this.canvas.width, this.canvas.height);
        nowtime = (window.serverTime() - this.delay) / 1000;
        if (this.frames.length > 1) {
          for (i = _i = 1, _ref = this.frames.length; 1 <= _ref ? _i < _ref : _i > _ref; i = 1 <= _ref ? ++_i : --_i) {
            if (this.frames[i].time + BUFFERED > nowtime) {
              frame = this.frames[i - 1];
              if ((this.__current_frame == null) || this.__current_frame !== frame) {
                this.onCurrentFrameChange(this.__current_frame, frame);
                this.__current_frame = frame;
              }
              break;
            }
          }
        } else {
          frame = this.frames[0];
          if ((this.__current_frame == null) || this.__current_frame !== frame) {
            this.onCurrentFrameChange(this.__current_frame, frame);
            this.__current_frame = frame;
          }
        }
        left = (nowtime - this.frames[0].time) * this.speed * -1;
        while (this.offset() + left + this.frames[0].image.width < 0) {
          this.frames.splice(0, 1);
          if (this.frames[0] == null) {
            return;
          }
          left = (nowtime - this.frames[0].time) * this.speed * -1;
        }
        right = this.offset() + left;
        _ref1 = this.frames;
        for (_j = 0, _len = _ref1.length; _j < _len; _j++) {
          frame = _ref1[_j];
          this.context.drawImage(frame.image, right - this.overlap, 0);
          right += frame.image.width - this.overlap;
        }
        return this.setPlayerColor();
      }
    };

    Waveform.prototype.title = function() {
      if (this.__current_frame != null) {
        return this.__current_frame.title;
      } else {
        return "Buffering...";
      }
    };

    Waveform.prototype.__dec2hex = function(i) {
      return (i + 0x100).toString(16).substr(-2);
    };

    Waveform.prototype.LIGHTENING = 32;

    Waveform.prototype.setPlayerColor = function() {
      var b, g, pix, r, _ref;
      pix = this.context.getImageData(this.offset(), parseInt(this.canvas.height / 2), 1, this.canvas.height).data;
      _ref = [Math.min(pix[0] + this.LIGHTENING, 255), Math.min(pix[1] + this.LIGHTENING, 255), Math.min(pix[2] + this.LIGHTENING, 255)], r = _ref[0], g = _ref[1], b = _ref[2];
      window.threeSixtyPlayer.config.playRingColor = "#" + (this.__dec2hex(r)) + (this.__dec2hex(g)) + (this.__dec2hex(b));
      return window.threeSixtyPlayer.config.backgroundRingColor = window.threeSixtyPlayer.config.playRingColor;
    };

    Waveform.prototype.onNewFrame = function(frame) {
      this.frames.push(frame);
      return frame.render();
    };

    Waveform.prototype.onCurrentFrameChange = function(old, knew) {
      if (knew.action === "Crossmatch" || knew.action === "Crossfade" || ((old != null) && (old.action === "Playback" && knew.action === "Playback"))) {
        return setTimeout(function() {
          knew.render();
          if (old != null) {
            return old.render();
          }
        }, (knew.action === "Crossmatch" ? knew.duration * 500 : 10));
      }
    };

    Waveform.prototype.process = function(f, from_socket) {
      var frame, img, me;
      frame = new Frame(f, from_socket);
      img = new Image;
      me = this;
      img.onload = function() {
        frame.image = this;
        if (window.__spinning) {
          window.__spinner.stop();
          window.__spinning = false;
        }
        return me.onNewFrame(frame);
      };
      return img.src = frame.waveform;
    };

    return Waveform;

  })();

  if (window.location.toString().search("beta.forever.fm") !== -1) {
    SC.initialize({
      client_id: "cd8a7092051937ab1994fa3868edb911",
      redirect_uri: "http://beta.forever.fm/static/sc.html"
    });
  } else {
    SC.initialize({
      client_id: "b08793cf5964f5571db86e3ca9e5378f",
      redirect_uri: "http://forever.fm/static/sc.html"
    });
  }

  connectedly = function(callback, authenticate) {
    var token;
    if (SC.isConnected()) {
      return callback();
    } else {
      token = localStorage.getItem("accessToken");
      if (token != null) {
        SC.accessToken(token);
        return getPersistent(callback);
      } else if ((authenticate == null) || authenticate) {
        return SC.connect(function(a) {
          if (typeof localStorage !== "undefined" && localStorage !== null) {
            localStorage.setItem('accessToken', SC.accessToken());
          }
          return getPersistent(callback);
        });
      }
    }
  };

  getPersistent = function(callback) {
    var _downloaded;
    _downloaded = localStorage.getItem("downloaded");
    if (_downloaded != null) {
      SC.downloaded = _downloaded.split(',');
    } else {
      SC.downloaded = [];
      localStorage.setItem('downloaded', SC.downloaded.join(','));
    }
    return SC.get("/me/favorites/", {
      limit: 1000
    }, function(favoriteds) {
      var track;
      SC.favorites = (function() {
        var _i, _len, _results;
        _results = [];
        for (_i = 0, _len = favoriteds.length; _i < _len; _i++) {
          track = favoriteds[_i];
          _results.push(track.id);
        }
        return _results;
      })();
      return callback(SC.favorites);
    });
  };

  Titular = (function() {
    Titular.prototype.char = "\u25b6";

    function Titular() {
      this.title = document.title;
      this.__title = "";
      this.rotation = 0;
      this.drawloop();
    }

    Titular.prototype.drawloop = function() {
      var me;
      this.draw();
      me = this;
      if (this.stop != null) {
        return;
      }
      return setTimeout((function() {
        return me.drawloop();
      }), 400);
    };

    Titular.prototype.draw = function(playing) {
      var s;
      if (playing == null) {
        s = window.soundManager.sounds.ui360Sound0;
        playing = (s != null) && s.playState === 1 && !s.paused;
      }
      if (playing) {
        return document.title = this.char + " " + this.rot(window._waveform.title());
      } else {
        return document.title = this.title;
      }
    };

    Titular.prototype.rot = function(title) {
      var r;
      if (title !== this.__title) {
        this.rotation = 0;
        this.__title = title;
      }
      if (this.rotation === this.__title.length) {
        this.rotation = 0;
      }
      r = this.__title.slice(this.rotation, this.__title.length) + " " + this.__title.slice(0, this.rotation);
      this.rotation += 1;
      return r;
    };

    return Titular;

  })();

  window.replace_h2 = function(tag, text) {
    if (tag.html() === text) {
      return;
    }
    tag.css('opacity', 0);
    return setTimeout(function() {
      tag.html(text);
      return tag.css('opacity', 1);
    }, 500);
  };

  format_uptime = function(seconds) {
    var days, hours, months, weeks, years;
    hours = Math.round(seconds / 3600);
    if (hours < 24) {
      return "" + hours + " hour" + (hours === 1 ? '' : 's');
    }
    days = Math.round(seconds / 86400);
    if (days < 7) {
      return "" + days + " day" + (days === 1 ? '' : 's');
    }
    weeks = Math.round(seconds / 604800);
    if (weeks < 4) {
      return "" + weeks + " week" + (weeks === 1 ? '' : 's');
    }
    months = Math.round(seconds / 2419200);
    if (months < 12) {
      return "" + months + " month" + (months === 1 ? '' : 's');
    }
    years = Math.round(seconds / 29030400);
    return "" + years + " year" + (years === 1 ? '' : 's');
  };

  window.rotate_h2 = function() {
    var tag;
    tag = $('h2');
    if (window.__original_h2 == null) {
      window.__original_h2 = tag.html();
    }
    return setInterval(function() {
      var toggle, uptime;
      toggle = tag.data('toggle');
      if (toggle != null) {
        switch (toggle) {
          case 0:
            window.replace_h2(tag, window.__original_h2);
            break;
          case 1:
            if ((window._listeners != null) && window._listeners > MIN_LISTENERS) {
              window.replace_h2(tag, "" + window._listeners + " listeners");
            }
            break;
          case 2:
            if (window._started_at != null) {
              uptime = ((+(new Date)) / 1000) - window._started_at;
              if (uptime > 86400) {
                window.replace_h2(tag, "up for " + (format_uptime(uptime)));
              }
            }
        }
      } else {
        toggle = 0;
      }
      toggle = (toggle + 1) % 3;
      return tag.data('toggle', toggle);
    }, 5000);
  };

  $(document).ready(function() {
    var getPing, s, w;
    window.rotate_h2();
    window.__spinner.spin(document.getElementById('content'));
    window.__spinning = true;
    window.__titular = new Titular;
    window.__heartbeat = $('#endpoint_link').attr('href').replace('all.mp3', 'heartbeat');
    $('body').keyup(function(e) {
      var s;
      s = window.soundManager.sounds.ui360Sound0;
      if (e.keyCode === 32) {
        if (s != null) {
          return s.togglePause();
        } else {
          return window.threeSixtyPlayer.handleClick({
            target: $('a.sm2_link')[0]
          });
        }
      }
    });
    setTimeout((function() {
      return $("#share").css("overflow", "visible");
    }), 2000);
    w = new Waveform(document.getElementById("waveform"));
    connectedly(function() {
      var id, _i, _j, _len, _len1, _ref, _ref1, _results;
      _ref = SC.favorites;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        id = _ref[_i];
        $("#track_" + id + " .like").addClass('selected');
      }
      _ref1 = SC.downloaded;
      _results = [];
      for (_j = 0, _len1 = _ref1.length; _j < _len1; _j++) {
        id = _ref1[_j];
        _results.push($("#track_" + id + " a.download").addClass('selected'));
      }
      return _results;
    }, false);
    $(window).resize(function() {
      w.layout();
      return w.draw();
    });
    $.getJSON("all.json", function(segments) {
      var segment, _i, _len, _results;
      _results = [];
      for (_i = 0, _len = segments.length; _i < _len; _i++) {
        segment = segments[_i];
        _results.push(w.process(segment));
      }
      return _results;
    });
    getPing = function() {
      var start_time;
      start_time = +(new Date);
      return $.getJSON("timing.json", function(data) {
        return window.ping = start_time - data.time;
      });
    };
    window.getPing = getPing;
    setInterval(getPing, TIMING_INTERVAL);
    getPing();
    s = io.connect(":8193/info.websocket");
    s.on('message', function(data) {
      if (typeof data === "string") {
        data = JSON.parse(data);
      }
      if (data.segment != null) {
        return w.process(data.segment, true);
      } else if (data.listener_count != null) {
        return window._listeners = data.listener_count;
      }
    });
    $(document).on("click", 'a.like', function(e) {
      var liked, me, trackid;
      e.preventDefault();
      me = this;
      trackid = parseInt($(this).data('track'));
      liked = $(this).hasClass('selected');
      $(me).toggleClass('selected');
      return connectedly(function() {
        if (liked) {
          return SC["delete"]("/me/favorites/" + trackid, function(a) {
            var idx, target;
            if (a.status != null) {
              target = $("#track_" + trackid + " .favoritings");
              target.html(comma(parseInt(target.html().replace(',', '')) - 1));
              idx = SC.favorites.indexof(trackid);
              if (idx > -1) {
                return SC.favorites.splice(idx, 1);
              }
            } else {
              return $(me).toggleClass('selected');
            }
          });
        } else {
          return SC.put("/me/favorites/" + trackid, function(a) {
            var target;
            if (a.status != null) {
              target = $("#track_" + trackid + " .favoritings");
              target.html(comma(parseInt(target.html().replace(',', '')) + 1));
              return SC.favorites.push(trackid);
            } else {
              return $(me).toggleClass('selected');
            }
          });
        }
      });
    });
    $(document).on("click", 'a.share', function(e) {
      var l, link, t, _h, _ref, _ref1, _w;
      e.preventDefault();
      _ref = [500, 250], _w = _ref[0], _h = _ref[1];
      _ref1 = [screen.width / 2 - (_w / 2), screen.height / 2 - (_h / 2)], l = _ref1[0], t = _ref1[1];
      link = w.__current_frame.twitter();
      window.open(link, "Twitter", "toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=no, resizable=yes,copyhistory=no,height=" + _h + ",width=" + _w + ",top=" + t + ",left=" + l);
      return $(this).addClass('selected');
    });
    $(document).on("click", 'a.download', function(e) {
      var me, trackid;
      e.preventDefault();
      trackid = parseInt($(this).data('track'));
      me = this;
      return connectedly(function() {
        var target;
        $(me).addClass('selected');
        me.href += "?oauth_token=" + (SC.accessToken());
        window.open(me.href, "Download");
        target = $("#track_" + trackid + " .stats .count.download");
        target.html(comma(parseInt(target.html().replace(',', '')) + 1));
        SC.downloaded.push(trackid);
        return localStorage.setItem('downloaded', SC.downloaded.join(','));
      });
    });
    $(document).on("click", 'a.jam', function(e) {
      return $(this).addClass('selected');
    });
    window._waveform = w;
    return window._socket = s;
  });

}).call(this);
