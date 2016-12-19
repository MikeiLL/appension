# Is this needed?
soundManager.setup
	url: '/static/flash/'

$(document).ready ->
	
	$('body').keyup (e) ->
		s = window.soundManager.sounds.ui360Sound0
		if e.keyCode == 32
			if s?
				s.toggleMute()
			else
				window.threeSixtyPlayer.handleClick {target: $('a.sm2_link')[0]}

	getTrackInfo = ->
		$.getJSON "http://localhost:8889/status.json", (info) ->
			tag = 0
			console.log("req " + req_time + " resp " + resp_time + " ts " + info.ts)
			for track in info.tracks
				console.log(track)
				id = track.id
					# To the subsequent maintainer: I apologize humbly - this is bad
					# code. I am not a CoffeeScript programmer, and it shows. The
					# idea here (and you're *most* welcome to edit the code to better
					# express that) is to have the first new track ID go into
					# artist0, the next new track ID go into artist1, etc; any track
					# with the same ID as a previously-seen track will be ignored.
					# Signed: Chris Angelico (Rosuav).
				# console.log("Track [" + track.id + "] start " + track.start_time + " end " + (track.start_time + track.details.length) + " now " + info.ts);
				if info.ts > track.start_time + track.details.length
					console.log("Track ["+id+"] is in the past")
					continue # Voorbij is nu voorbij :)
				else
					console.log("Track ["+id+"] is in the future")
				if track.details.url
					track_url = ''
				else
					track_url = '<a href="http://'+track.details.url+'" target="_blank">'+track.details.url+'</a>'

				if track.details.story
					story = track.details.story.replace(/\r?\n|\r+|\r/g, "<br/>");
				else
					story = "The story behind this track is still a mystery. Please let us know if you can solve."
				minutes = Math.floor(track.details.length/60)
				seconds = Math.floor(track.details.length%60)
				if seconds < 10
					seconds = "0" + seconds
				tag += 1
				artist = document.getElementById('artist'+tag)
				if artist
					# Eventually we'll run out of objects to stash info into - that's fine.
					# Assume that every artistN has corresponding other stash-targets lengthN
					# and (eventually) titleN.
					artist.innerHTML = track.details.artist
					document.getElementById('story'+tag).innerHTML = story + '<div class="track_url">' + track_url + '</div>'
					document.getElementById('length'+tag).innerHTML = minutes + ":" + seconds
			while 1
				tag = tag + 1
				artist = document.getElementById('artist'+tag)
				if artist
					artist.innerHTML = ""
					document.getElementById('length'+tag).innerHTML = "Chunk digging..."
					document.getElementById('story'+tag).innerHTML = "Still digging around in the chunk selector, dear. Sit tight! :)"
				else
					break
	setTimeout getTrackInfo, 1000
	setInterval getTrackInfo, 30000
