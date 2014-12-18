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
		console.log(matches)
		console.log(@artist)
		console.log(@title)
		
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
	
	$('body').keyup (e) ->
		s = window.soundManager.sounds.ui360Sound0
		if e.keyCode == 32
			if s?
				s.toggleMute()
			else
				window.threeSixtyPlayer.handleClick {target: $('a.sm2_link')[0]}

	getTrackInfo = ->
		$.getJSON "all.json", (segments) ->
			#console.log("getTrackInfo")
			#console.log(segments)
			trackids = []
			for segment in segments
				if segment.tracks?
					id = segment.tracks[0].metadata.id
					# To the subsequent maintainer: I apologize humbly - this is bad
					# code. I am not a CoffeeScript programmer, and it shows. The
					# idea here (and you're *most* welcome to edit the code to better
					# express that) is to have the first new track ID go into
					# artist0, the next new track ID go into artist1, etc; any track
					# with the same ID as a previously-seen track will be ignored.
					# Signed: Chris Angelico (Rosuav).
					now = window.serverTime()/1000
					if now > segment.time+segment.duration
						#console.log("Segment ["+id+"] is in the past")
						continue # Voorbij is nu voorbij :)
					else
						#console.log("Segment ["+id+"] is in the future")
					isnew = 1
					for t in trackids
						if t == id
							isnew = 0
					if isnew
						trackids.push(id)
						tag = trackids.length
						length = segment.tracks[0].metadata.length
						if segment.tracks[0].metadata.story
							story = segment.tracks[0].metadata.story
							console.log('have')
							console.log(story)
						else
							story = "This one is still a mystery. Please let us know if you can solve."
							console.log('empty')
							console.log(story)
						minutes = Math.floor(length/60)
						seconds = Math.floor(length%60)
						if seconds < 10
							seconds = "0" + seconds
						#console.log("Recording artist"+tag+" as "+segment.tracks[0].metadata.artist)
						artist = document.getElementById('artist'+tag)
						if artist
							# Eventually we'll run out of objects to stash info into - that's fine.
							# Assume that every artistN has corresponding other stash-targets lengthN
							# and (eventually) titleN.
							artist.innerHTML = segment.tracks[0].metadata.artist
							document.getElementById('story'+tag).innerHTML = story
							document.getElementById('length'+tag).innerHTML = minutes + ":" + seconds
				# console.log(segment.tracks[0].metadata)
				# console.log(segment.tracks[0].metadata.id)
			# Sorry, subsequent maintainer, more bad code here. -- Rosuav
			tag = trackids.length
			while 1
				tag = tag + 1
				artist = document.getElementById('artist'+tag)
				if artist
					artist.innerHTML = ""
					document.getElementById('length'+tag).innerHTML = ""
					# document.getElementById('story'+tag).innerHTML = ""
				else
					break
	setTimeout getTrackInfo, 1000
	setInterval getTrackInfo, TIMING_INTERVAL

	getPing = ->
		start_time = +new Date
		$.getJSON "timing.json", (data) ->
			window.ping = start_time - data.time
	window.getPing = getPing
	setInterval getPing, TIMING_INTERVAL
	getPing()


	getTrackDetails = ->
		s = io.connect ":8193/info.websocket"
		s.on 'message', (data) ->
			if typeof data is "string"
				data = JSON.parse(data)
				if data.segment.send_next_track
					#console.log("Send next track!")
					#console.log(Date())
					#console.log(data.segment.prev_track)
					#console.log(data.segment.next_track)
					# Temporarily tagging the artist so we know it came from send_next_track
					document.getElementById('artist').innerHTML = "[snt] " + data.segment.next_track.artist
					document.getElementById('artist_next').innerHTML = "Up next: (unknown)"
					length = data.segment.next_track.length
					minutes = Math.floor(length/60)
					seconds = Math.floor(length%60)
					if seconds < 10
						seconds = "0" + seconds
					document.getElementById('length').innerHTML = minutes + ":" + seconds
					return
				if data.segment.tracks[0].metadata.id != window._track_id
					window._track_id = data.segment.tracks[0].metadata.id
					# TODO Be safe against embedded HTML tags
					document.getElementById('artist').innerHTML = window._next_artist
					window._next_artist = data.segment.tracks[0].metadata.artist
					document.getElementById('artist_next').innerHTML = "Up next: " + window._next_artist
				#console.log("GetTrackDets Data " + window._count_TrackDeets + ": ")
				#console.log(data.segment.tracks[0].metadata.artist)
				#console.log(data.segment.tracks[0].metadata.id)
				window._count_TrackDeets++
			if data.listener_count?
				window._listeners = data.listener_count
		window._socket = s
	
	# setTimeout getTrackDetails, 1000 # Not in use currently
	window._count_getJSON = 1
	if not window._count_TrackDeets?
		window._count_TrackDeets = 1
