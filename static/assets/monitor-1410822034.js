(function() {
  var Queue, fetch, getBytesWithUnit, listeners, update;

  window.log = function() {
    log.history = log.history || [];
    log.history.push(arguments);
    if (this.console) {
      return console.log(Array.prototype.slice.call(arguments));
    }
  };

  Queue = (function() {
    Queue.all = {};

    function Queue(name, initdata) {
      this.name = name;
      this.initdata = initdata;
      Queue.all[this.name] = this;
      $('.queues').append("<div class=\"chart\" id=\"chart_" + this.name + "\">\n  <div class=\"name\">\n    " + this.name + "\n  </div>\n  <div class=\"bar\">\n    \n  </div>\n</div>");
      this.id = "chart_" + this.name;
      this.bar = $("#" + this.id + " .bar");
      this._name = $("#" + this.id + " .name");
      if (this.initdata != null) {
        this.update(this.initdata);
      }
    }

    Queue.prototype.update = function(raw) {
      this.data = raw;
      return this.redraw();
    };

    Queue.prototype.redraw = function() {
      var frames, minutes, seconds;
      frames = parseInt(this.data);
      this.bar.width(((frames / 9187) * 100) + "%");
      seconds = frames * (1152.0 / 44100.0);
      minutes = parseInt(seconds / 60);
      seconds = parseInt(seconds - 60 * minutes);
      this.bar.html("" + minutes + "m" + seconds + "s");
      return this._name.toggleClass('active');
    };

    return Queue;

  })();

  listeners = [];

  update = function(id, data) {
    var el;
    el = $(document.getElementById(id));
    console.log("Updating " + id + ": " + el);
    $('.url', el).html(data.config.relay_url);
    $('.location', el).html(data.config.relay_location);
    $('.started', el).html(data.started_at);
    $('.started', el).attr('title', (new Date(data.started_at)).toISOString());
    $('.started', el).timeago();
    $('.listeners', el).html(data.listeners);
    $('.bytes_out_month', el).html(getBytesWithUnit(data.bytes_out_month));
    $('.bytes_in_month', el).html(getBytesWithUnit(data.bytes_in_month));
    $('.peak_bytes_out_month', el).html(getBytesWithUnit(data.peaks.bytes_out_month));
    return $('.peak_listeners', el).html(data.peaks.listeners);
  };

  fetch = function(url, id) {
    return $.getJSON(url, function(data) {
      update(id, data);
      return setTimeout((function() {
        return fetch(url, id);
      }), 10 * 1000);
    });
  };

  getBytesWithUnit = function(bytes) {
    var amountOf2s, i, units;
    if (isNaN(bytes)) {
      return;
    }
    units = [" bytes", " KB", " MB", " GB", " TB", " PB", " EB", " ZB", " YB"];
    amountOf2s = Math.floor(Math.log(+bytes) / Math.log(2));
    if (amountOf2s < 1) {
      amountOf2s = 0;
    }
    i = Math.floor(amountOf2s / 10);
    bytes = +bytes / Math.pow(2, 10 * i);
    if (bytes.toString().length > bytes.toFixed(3).toString().length) {
      bytes = bytes.toFixed(3);
    }
    return bytes + units[i];
  };

  $(document).ready(function() {
    var s;
    s = io.connect(":8193/monitor.websocket");
    s.on('message', function(data) {
      var id, json, k, l, v, _i, _len, _ref, _ref1, _results;
      _ref = data.listeners;
      for (_i = 0, _len = _ref.length; _i < _len; _i++) {
        l = _ref[_i];
        if ('X-Forwarded-For' in l) {
          id = l['X-Forwarded-For'].replace(/\./g, '');
          json = l['X-Relay-Addr'] + "/?callback=?";
          if (document.getElementById(id) === null) {
            $('.relays').append("<div class=\"relay\" id=\"" + id + "\">\n  <h1 class=\"url\"></h1>  \n  <h2 class=\"location\"></h2>\n  <div>Started: <span class=\"started\"></span></div>\n  <div><span class=\"listeners\"></span> listeners</div>\n  <div><span class=\"bytes_out_month\"></span> sent this month</div>\n  <div><span class=\"bytes_in_month\"></span> rec'd this month</div>\n  <div><br /></div>\n  <div><span class=\"peak_listeners\"></span> listeners (at peak)</div>\n  <div><span class=\"peak_bytes_out_month\"></span> sent (at peak month)</div>\n  <div style=\"clear: both\"></div>\n</div>");
            fetch(json, id);
          }
        }
      }
      $('.info .started span.v').html(new Date(data.info.started * 1000).toISOString());
      if ($('.info .started span.ago').attr('title') == null) {
        $('.info .started span.ago').attr('title', new Date(data.info.started * 1000).toISOString());
        $('.info .started span.ago').timeago();
      }
      $('.info .samples span.v').html(data.info.samples + " samples");
      $('.info .samples span.sec').html(Math.round(data.info.samples * 100 / 44100.0) / 100.0);
      $('.info .duration span.v').html(data.info.duration + " seconds");
      $('.info .duration span.delta').html((data.info.duration - (data.info.samples / 44100.0)) + " seconds");
      $('.info .width span.v').html(data.info.width + "px");
      $('.info .width span.delta').html(((data.info.width / 5.0) - (data.info.samples / 44100.0)) + " seconds");
      _ref1 = data.queues;
      _results = [];
      for (k in _ref1) {
        v = _ref1[k];
        if (!(k in Queue.all)) {
          _results.push(new Queue(k, v));
        } else {
          _results.push(Queue.all[k].update(v));
        }
      }
      return _results;
    });
    return window._s = s;
  });

}).call(this);
