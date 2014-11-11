window.log = ->
  log.history = log.history or []
  log.history.push arguments
  console.log Array::slice.call(arguments)  if @console


soundManager.setup
  url: '/static/flash/'

TIMING_INTERVAL = 30000 # ms between checking server ping
NUM_TRACKS = 5

#   Empirical.
OFFSET = 5
BUFFERED = OFFSET

MIN_LISTENERS = 30

DONE_TRACKS_LIMIT = 8
MAGIC_REGEX = /(\s*-*\s*((\[|\(|\*|~)[^\)\]]*(mp3|dl|description|free|download|comment|out now|clip|bonus|preview|teaser|in store|follow me|follow on|prod|full|snip|exclusive|beatport|original mix)+[^\)\]]*(\]|\)|\*|~)|((OUT NOW( ON \w*)?|free|download|preview|follow me|follow on|teaser|in store|mp3|dl|description|full|snip|exclusive|beatport|original mix).*$))\s*|\[(.*?)\])/i

comma = (x) ->
  if x? then x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',') else x

window.ping = 0
window.serverTime = -> (+new Date) - window.ping

class Frame
  constructor: (init, is_new) ->
    for k, v of init
      this[k] = v
    @image = null
    @div = null
    @id = "track_#{@tracks[0].metadata.id}"
    @new = if is_new then 'new' else ''
    # hack for development... don't wanna do this
    while document.getElementById(@id)
      @id += "_"

    @parseMetaData()

  parseMetaData: ->
    matches = @tracks[0].metadata.title.match(/(.*?) by (.*)/i)
    if matches?
      [_, @title, @artist] = matches
      matches = @artist.match(/(.*?)\s+-\s+(.*)/i)
      [_, @artist, other] = matches if matches?
    else
      matches = @tracks[0].metadata.title.match(/(.*?)\s*-\s+(.*)/i)
      if matches?
        [_, @artist, @title] = matches
      else
        @title = @tracks[0].metadata.title
        @artist = @tracks[0].metadata.artist
    
    matches = @title.match(/([^\[\]]*?)( - ([^\[\]\(\)]*)|(\[.*\]))/i)
    if matches?
      [_, @title, _, other] = matches
    
    #   Try to remove "Free Download," "Follow Me" and the like
    _title = @title.replace MAGIC_REGEX, ""
    @title = _title if _title.length > 0

    _artist = @artist.replace MAGIC_REGEX, ""
    @artist = _artist if _artist.length > 0

    if @title[0] == '"' and @title[@title.length - 1] == '"'
      @title = @title[1...@title.length - 1].trim()

    #@img = if @tracks[0].metadata.artwork_url?
    #         @tracks[0].metadata.artwork_url
    #       else
    #         @tracks[0].metadata.user.avatar_url


    # Buttons
    @buttons = true
    @nid = @tracks[0].metadata.id


    @url = @tracks[0].metadata.permalink_url


  html: (first) ->
    first = false if not first?
    _new = @new
    @new = ''
    """
    <div class='track #{_new} #{if @played() and not first then "hidden" else ""}' id='#{@id}' target="_blank" href="#{@url}">
      <a class="coverart" href="#{@url}" target="_blank"><img src="#{@img}" /></a>
      <div class="text">
        <a class="title" href="#{@url}" target="_blank">#{@title}</a>
        <span class="artist">#{@artist}</span>
      </div>

      #{if @stats then "
     <h2>NOTHING</h2>
      " else ""}
    </div>
    """

  played: ->
    (@time + @duration + BUFFERED) < (window.serverTime() / 1000)

  playing: ->
    ((@time + BUFFERED) < (window.serverTime() / 1000)) and not @played()

  intendedParent: ->
    document.getElementById( if @played() then "done" else "tracks" )

  render: ->
    return if @action != "Playback"
    return @relayout() if @div?

    parent = @intendedParent()
    $(parent).prepend @html(true)
    id = @id
    setTimeout((-> $("##{id}").removeClass 'new hidden'), 100)
    @div = document.getElementById @id

  relayout: ->
    @div = document.getElementById(@id) if not @div.parentNode?
    newparent = document.getElementById( if @played() then "done" else "tracks" )
    if @div.parentNode != newparent
      neighbour = @div.parentNode.children[@div.parentNode.children.length - 2]
      $(@div).addClass("ending")
      $(neighbour).addClass("next")

      div = @div
      html = @html()
      setTimeout ->
        $(neighbour).removeClass("next")
        div.parentNode.removeChild div
        newparent.innerHTML = html + newparent.innerHTML
        setTimeout ->
          $(".hidden", newparent).removeClass('hidden')
          if newparent.children.length > DONE_TRACKS_LIMIT
            end = newparent.children[newparent.children.length - 1]
            $(end).addClass('hidden')
            setTimeout ->
              newparent.removeChild end
            , 1000
        , 100
      , 1400

class Waveform
  speed: 5
  constructor: (@canvas) ->
    @delay = 0
    @_offset = $("#menu").outerWidth()
    @frames = []
    @context = @canvas.getContext "2d"
    @overlap = if navigator.userAgent.match(/chrome/i)? then 0 else 1
    @layout()
    @drawloop()

  offset: ->
    @_offset + @buffered()

  buffered: ->
    ((window.threeSixtyPlayer.bufferDelay) * @speed / 1000.0) + OFFSET

  layout: ->
    @canvas.width = window.innerWidth

  drawloop: ->
    @draw()
    me = this
    return if @stop?
    setTimeout((-> me.drawloop()), 100)

  draw: ->
    BUFFERED = @buffered()
    if window.soundManager.sounds.ui360Sound0? && window.soundManager.sounds.ui360Sound0.paused
      @paused_at = window.serverTime() unless @paused_at?
      return
    else if @paused_at?
      @delay += (window.serverTime() - @paused_at)
      delete @paused_at

    if @frames[0]?
      @context.clearRect 0, 0, @canvas.width, @canvas.height
      nowtime = (window.serverTime() - @delay) / 1000
      
      if @frames.length > 1
        for i in [1...@frames.length]
          if @frames[i].time + BUFFERED > nowtime
            frame = @frames[i-1]
            if not @__current_frame? || @__current_frame != frame
              @onCurrentFrameChange @__current_frame, frame
              @__current_frame = frame
            break
      else
        frame = @frames[0]
        if not @__current_frame? || @__current_frame != frame
          @onCurrentFrameChange @__current_frame, frame
          @__current_frame = frame


      left = (nowtime - @frames[0].time) * @speed * -1
      while @offset() + left + @frames[0].image.width < 0
        @frames.splice(0, 1)
        return if not @frames[0]?
        left = (nowtime - @frames[0].time) * @speed * -1
      right = @offset() + left

      # Actually draw our waveform here
      for frame in @frames
        @context.drawImage frame.image, right - @overlap, 0
        #if @overlap > 0
          # Clone the last column to prevent visual artifacts on Safari/Firefox
        # @context.putImageData(@context.getImageData(right - @overlap, 0, @overlap, @canvas.height), right, 0)
        right += frame.image.width - @overlap
      @setPlayerColor()

  title: ->
    if @__current_frame? then @__current_frame.title else "Buffering..."

  __dec2hex: (i) ->
   (i+0x100).toString(16).substr(-2)

  LIGHTENING: 32
  setPlayerColor: ->
    pix = @context.getImageData(@offset(), parseInt(@canvas.height / 2), 1, @canvas.height).data
    [r, g, b] = [Math.min(pix[0] + @LIGHTENING, 255),
                 Math.min(pix[1] + @LIGHTENING, 255),
                 Math.min(pix[2] + @LIGHTENING, 255)]
    window.threeSixtyPlayer.config.playRingColor = "##{@__dec2hex(r)}#{@__dec2hex(g)}#{@__dec2hex(b)}"
    window.threeSixtyPlayer.config.backgroundRingColor = window.threeSixtyPlayer.config.playRingColor

  onNewFrame: (frame) ->
    @frames.push frame
    frame.render()
    
  onCurrentFrameChange: (old, knew) ->
    if knew.action == "Crossmatch" or knew.action == "Crossfade" or (old? and (old.action == "Playback" and knew.action == "Playback"))
      setTimeout ->
        knew.render()
        old.render() if old?
      , (if knew.action == "Crossmatch" then knew.duration * 500 else 10)
    
  process: (f, from_socket) ->
    frame = new Frame f, from_socket
    img = new Image
    me = this
    img.onload = ->
      frame.image = this
      if window.__spinning
        window.__spinner.stop()
        window.__spinning = false
      me.onNewFrame frame
    img.src = frame.waveform


class Titular
  char: "\u25b6"
  constructor: ->
    @title = document.title
    @__title = ""
    @rotation = 0
    @drawloop()

  drawloop: ->
    @draw()
    me = this
    return if @stop?
    setTimeout((-> me.drawloop()), 400)

  draw: (playing) ->
    if not playing?
      s = window.soundManager.sounds.ui360Sound0
      playing = (s? and s.playState == 1 and not s.paused)
    document.title = @title

  rot: (title) ->
    if title != @__title
      @rotation = 0
      @__title = title
    if @rotation == @__title.length
      @rotation = 0
    r = @__title[@rotation...@__title.length] + " " + @__title[0...@rotation]
    @rotation += 1
    r

window.replace_h2 = (tag, text) ->
  return if tag.html() == text
  tag.css 'opacity', 0
  setTimeout ->
    tag.html(text)
    tag.css 'opacity', 1
  , 500


format_uptime = (seconds) ->
  hours = Math.round(seconds / 3600)
  return "#{hours} hour#{if hours == 1 then '' else 's'}" if hours < 24
  days = Math.round(seconds / 86400)
  return "#{days} day#{if days == 1 then '' else 's'}" if days < 7
  weeks = Math.round(seconds / 604800)
  return "#{weeks} week#{if weeks == 1 then '' else 's'}" if weeks < 4
  months = Math.round(seconds / 2419200)
  return "#{months} month#{if months == 1 then '' else 's'}" if months < 12
  years = Math.round(seconds / 29030400)
  return "#{years} year#{if years == 1 then '' else 's'}"

window.rotate_h2 = ->
  tag = $('h2')
  window.__original_h2 = tag.html() if not window.__original_h2?
  setInterval ->
    toggle = tag.data('toggle')
    if toggle?
      switch toggle
        when 0
          window.replace_h2 tag, window.__original_h2
        when 1
          if window._listeners? and window._listeners > MIN_LISTENERS
            window.replace_h2 tag, "#{window._listeners} listeners"
        when 2
          if window._started_at?
            uptime = ((+new Date) / 1000) - window._started_at
            if uptime > 86400
              window.replace_h2 tag, "up for #{format_uptime uptime}"
    else
      toggle = 0
    toggle = (toggle + 1) % 3
    tag.data('toggle', toggle)
  , 5000

$(document).ready ->
  window.rotate_h2()
  window.__spinner.spin document.getElementById('content')
  window.__spinning = true
  window.__titular = new Titular
  window.__heartbeat = $('#endpoint_link').attr('href').replace('all.mp3', 'heartbeat')
  w = new Waveform document.getElementById "waveform"
  
  $('body').keyup (e) ->
    s = window.soundManager.sounds.ui360Sound0
    if e.keyCode == 32
      if s?
        s.togglePause()
      else
        window.threeSixtyPlayer.handleClick {target: $('a.sm2_link')[0]}

  $.getJSON "all.json", (segments) ->
    for segment in segments
      # console.log("getJSON here")
      w.process segment

  getPing = ->
    start_time = +new Date
    $.getJSON "timing.json", (data) ->
      window.ping = start_time - data.time
  window.getPing = getPing
  setInterval getPing, TIMING_INTERVAL
  getPing()


  root = exports ? this
  root.getTrackDetails = ->
    console.log("You pressed me.")
    s = io.connect ":8193/info.websocket"
    s.on 'message', (data) ->
      if typeof data is "string"
        data = JSON.parse(data)
        console.log(data.segment.tracks[0].metadata.artist)
        console.log(data.segment.tracks[0].metadata.title)
        console.log(data.segment.duration)
      if data.listener_count?
        window._listeners = data.listener_count
      console.log "something happened."
    window._socket = s
	
  window._waveform = w