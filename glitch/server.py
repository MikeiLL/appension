from flask import Flask, render_template, request, redirect, url_for, Response, send_from_directory, jsonify, flash
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.urls import url_quote_plus
from urllib.parse import urlparse, urljoin
import os
import sys
import time
import logging
import datetime
import random
import functools
import subprocess
from . import apikeys, config, database, oracle, utils, mailer

app = Flask(__name__)

# In production mode, the renderer runs on port 81. In debug, it's on 8889.
renderer_port = 81

UPLOAD_FOLDER = 'uploads'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_get"
app.config["SECRET_KEY"] = apikeys.cookie_monster
ALLOWED_EXTENSIONS = set(['mp3', 'png', 'jpg', 'jpeg', 'gif'])

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@login_manager.user_loader
def load_user(id):
	return database.User.from_id(int(id))

@app.template_filter()
def format_seconds(value):
	return datetime.timedelta(seconds=int(value))

# from http://flask.pocoo.org/snippets/62/
def is_safe_url(target):
	ref_url = urlparse(request.host_url)
	test_url = urlparse(urljoin(request.host_url, target))
	return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc

started_at_timestamp = time.time()
started_at = datetime.datetime.utcnow()

page_title = "Infinite Glitch - The World's Longest Recorded Pop Song, by Chris Butler."
og_description = """I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""
meta_description = """I don't remember if he said it or if I said it or if the caffeine said it but suddenly we're both giggling 'cause the problem with the song isn't that it's too long it's that it's too short."""

def admin_required(func):
	"""Like login_required but also checks for admin access"""
	@login_required
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		logging.warn("Current user being checked")
		if current_user.user_level < 2:
			logging.warn("Current user is less than level two: %r" % (current_user))
			# TODO: Different error page for non-admin?
			return login_manager.unauthorized()
		logging.warn("Current user is at least level two: %r" % (current_user))
		return func(*args, **kwargs)
	return wrapper

def couplet_count(lyrics):
	total = 0
	for count in lyrics:
		total += count.track_lyrics['couplet_count']
	return total

@app.route("/")
def home():
	lyrics = database.get_all_lyrics()
	complete_length = datetime.timedelta(seconds=int(database.get_complete_length()))
	prot = "https" if os.path.exists("privkey.pem") else "http" # TODO: See if the incoming request was over HTTPS instead
	return render_template("index.html",
		open=True, # Can have this check for server load if we ever care
		renderer="%s://%s:%d/" % (prot, urlparse(request.url_root).netloc.split(":")[0], renderer_port),
		complete_length=complete_length,
		couplet_count=couplet_count(lyrics),
		lyrics=lyrics,
		og_url=config.server_domain,
		og_description=og_description,
		meta_description=meta_description
	)

def _make_route(dir):
	# Use a closure to early-bind the 'dir'
	def non_caching_statics(path):
		response = send_from_directory("../"+dir, path)
		response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
		response.headers['Pragma'] = 'no-cache'
		return response
	app.add_url_rule('/'+dir+'/<path:path>', 'non_caching_'+dir, non_caching_statics)
for _dir in ("audio", "audition_audio", "transition_audio", ".well-known"):
	# audition_audio and transition_audio aren't currently used, but
	# will be part of the admin panel that we haven't yet ported.
	_make_route(_dir)

@app.route("/static/flash/soundmanager2_flash9.swf")
def sm_flash():
	return send_from_directory("static/flash", 'soundmanager2_flash9.swf', mimetype='application/x-shockwave-flash', attachment_filename='soundmanager2_flash9.swf', as_attachment=False)

@app.route("/robots.txt")
def robots_txt():
	return send_from_directory("static/", 'robots.txt', mimetype='text/*', attachment_filename='robots.txt', as_attachment=False)

@app.route("/artwork/<int:id>.jpg")
def track_artwork(id):
	art = database.get_track_artwork(int(id))
	# TODO: If the track hasn't been approved yet, return 404 unless the user is an admin.
	if not art:
		return redirect('../static/img/Default-artwork-200.png')
	return bytes(art)

@app.route("/timing.json")
def timing():
	return jsonify({"time": time.time() * 1000})

@app.route("/credits")
def credits():
	og_description="The world's longest recorded pop song. (Credits)"
	page_title="Credits: Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
	meta_description="The people below are partially responsible for bringing you Infinite Glitch - the world's longest recorded pop song."
	og_url="http://www.infiniteglitch.net/credits"
	return render_template("credits.html",
				og_description=og_description, page_title=page_title,
				meta_description=meta_description,og_url=og_url)

@app.route("/view_artist/<artist>")
def tracks_by_artist(artist):
	# TODO: Clean up the whole sposplit/fposplit stuff, maybe by slash-separating
	artist_for_db = url_artist = artist
	if artist[:8] == 'sposplit':
		artist = artist[9:]
		artist_formatting = artist.split('fposplit',1)
		artist_for_db = ', '.join([part.strip() for part in artist_formatting])
		artist = ' '.join([part.strip() for part in artist_formatting[::-1]])
	tracks_by = database.tracks_by(artist_for_db)
	og_description= artist+" contributions to The world's longest recorded pop song."
	page_title=artist+": Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
	meta_description="Browse the artists who have added to the Infinite Glitch - the world's longest recorded pop song."
	og_url = url_for("tracks_by_artist", artist=url_artist)
	return render_template("view_artist.html", tracks_by=tracks_by, og_description=og_description,
				page_title=page_title, meta_description=meta_description, og_url=og_url)


@app.route("/choice_chunks")
def choice_chunks():
	og_description= "You can select any individual chunk of The Infinite Glitch to listen to."
	page_title="Browse Artists: Infinite Glitch - the world's longest recorded pop song, by Chris Butler."
	meta_description="You can select any individual chunk of The Infinite Glitch to listen to."
	og_url=config.server_domain+"/choice_chunks"
	letter = request.args.get("letters", "")
	print(letter)
	if letter:
		artist_tracks = database.browse_tracks(letter)
		ordered_artists = utils.alphabetize_ignore_the(artist_tracks)
	else:
		ordered_artists = ""
	recent_submitters = database.get_recent_tracks(10)
	ordered_submitters = utils.alphabetize_ignore_the(recent_submitters)
	return render_template("choice_chunks.html", recent_submitters=ordered_submitters, artist_tracks=ordered_artists, letter=letter,
				og_description=og_description, page_title=page_title, meta_description=meta_description, og_url=og_url)

@app.context_processor
def inject_now():
    return {'now': datetime.datetime.utcnow()}

@app.route("/login")
def login_get():
	return render_template("login.html")

@app.route("/login", methods=["POST"])
def login_post():
	logging.info("in login post")
	user = database.User.from_credentials(request.form["email"], request.form["password"])
	logging.info(user)
	if user: login_user(user)
	url = request.args.get("next") or "/"
	logging.info(url)
	url_test = is_safe_url(url)
	logging.info("url test result: %r" % (url_test))
	if not is_safe_url(url): url = "/"
	return redirect(url)

@app.route("/logout")
def logout():
	logout_user()
	return redirect("/")

@app.route("/create_account")
def create_account_get():
	return render_template("create_account.html", page_title="Glitch Account Sign-Up")

@app.route("/create_account", methods=["POST"])
def create_account_post():
	if request.form["spamtest"] != "Ringo":
		return redirect("/create_account")
	if request.form["password"] != request.form["password2"]:
		return redirect("/create_account")
	info = database.create_user(request.form["username"], request.form["email"], request.form["password"])
	if isinstance(info, str):
		# There's an error.
		return render_template("create_account.html", page_title="Glitch Account Sign-Up", error=info)
	confirmation_url = request.base_url + "/confirm/%s/%s" % info # yes, that's "/create_account/confirm"
	user_message = """Either you or someone else just created an account at InfiniteGlitch.net.

To confirm for %s at %s, please visit %s""" % (request.form["username"], request.form["email"], confirmation_url)
	result = mailer.alert_message(user_message, 'Infinite Glitch Account', you=request.form["email"])
	if (result):
		return render_template("account_confirmation.html",
			notice="Thanks for joining our little gang. Please check your email for confirmation link... and click it.")
	else:
		return render_template("whoops.html",
			notice="There was a problem emailing the administrator.", admin=apikeys.admin_email)

@app.route("/create_account/confirm/<id>/<nonce>")
def confirm_account(id, nonce):
	user_name, user_email = database.confirm_user(id, nonce)
	if user_name is None:
		flash("Incorrect confirmation link, or link expired. Sorry!")
		return redirect("/")
	else:
		login_user(database.User.from_id(id))
		admin_message = "New user " + user_name + " created with email: " + user_email + "."
	mailer.alert_message(admin_message, 'New Infinite Glitch Account Created')
	user_message = """Welcome to the party, %s. Any questions, write to %s.""" % (user_name, apikeys.system_email)
	result = mailer.alert_message(user_message, 'Welcome, Infinite Glitch Participant', you=user_email)
	flash("Welcome, " + user_name + "! Your account has been confirmed.")
	return redirect("/")

@app.route("/reset_password")
def reset_password_get():
	return render_template("reset_password.html", page_title="Reset Glitch Account Password")

@app.route("/reset_password", methods=["POST"])
def reset_password_post():
	if not request.form["email"]:
		return redirect("/reset_password")
	info = database.request_password_reset(request.form["email"])
	if not info:
		flash("Unrecognized email address.")
		return redirect("/reset_password")
	confirmation_url = request.base_url + "/confirm/%s/%s" % info
	user_message = """Either you or someone else requested a password reset for InfiniteGlitch.net.

To confirm, please visit %s""" % confirmation_url
	result = mailer.alert_message(user_message, 'Infinite Glitch Account', you=request.form["email"])
	if (result):
		return render_template("account_confirmation.html",
			notice="Password reset link sent. Please check your email.")
	else:
		return render_template("whoops.html",
			notice="There was a problem emailing the administrator.", admin=apikeys.admin_email)

@app.route("/reset_password/confirm/<id>/<nonce>")
def select_password(id, nonce):
	valid_reset_link = database.select_new_password(id, nonce)
	if valid_reset_link is None:
		flash("Incorrect confirmation link, or link expired. Sorry!")
	else:
		return render_template("select_password.html",
			id=id, hex_key=nonce)

@app.route("/update_password/<id>/<nonce>", methods=['POST'])
def update_user_pass(id, nonce):
	user_update = database.reset_user_password(id, nonce, request.form["password"])
	if user_update is None:
		flash("Something went wrong. Sorry!")
	else:
		flash("Your password has been reset. You can now log in.")
	return redirect("/login")

@app.route("/submit")
@login_required
def submit_track_get():
	'''
	The following two forms are for user to submit a track.
	'''
	f = open('fortunes.txt', 'r')
	fortunes = [line for line in f if not line[0] == '%']
	saying = random.choice(fortunes)
	return render_template("submit_track.html", page_title="Infinite Glitch Track Submission Form", witty_saying=saying)

@app.route("/submit", methods=["POST"])
@login_required
def submit_track_post():
	# check if the post request has the file part
	if 'mp3_file' not in request.files:
		flash('No audio file uploaded')
		return redirect(request.url)
	file = request.files["mp3_file"]
	# if user does not select file, browser also
	# submit a empty part without filename
	if not file.filename:
		flash('No audio file uploaded')
		return redirect(request.url)
	if not file.filename.endswith('.mp3') or file.mimetype not in {"audio/mpeg", "audio/mp3"}:
		# TODO: Support more files
		# TODO: Test file content, not just extension
		logging.debug("Rejecting upload of %r [%s]", file.filename, file.mimetype)
		flash('Only .mp3 files currently accepted')
		return redirect(request.url)
	image = None # TODO
	id = database.create_track(file.read(), secure_filename(file.filename), request.form, image, current_user.username)
	# TODO: Send email to admins requesting curation (with the track ID)
	return render_template("confirm_submission.html")

# Deprecated
@app.route("/recorder")
@login_required
def recorder_get():
	return render_template("recorder.html", page_title="Infinite Glitch Recording Studio")

# Deprecated and may not be fully working
@app.route("/recorder", methods=["POST"])
@login_required
def recorder_post():
	try:
		print(request.files["data"])
	except:
		print ('not that')
	print(request.files.lists().next())
	# <generator object MultiDict.lists at 0x114c71a98>
	print(request.files.keys())
	# <dict_keyiterator object at 0x114c57278>
	print(request.files.values().next())
	# <generator object MultiDict.values at 0x114c71a98>
	print(current_user if current_user else 'glitch hacker')
	# <flask_login.mixins.AnonymousUserMixin object at 0x111216e80>
	return render_template("recorder.html")

@app.route("/oracle", methods=["GET"])
def oracle_get():
	popular_words = oracle.popular_words(90)
	random.shuffle(popular_words)
	question = request.args.get("question")
	if question:
		show_cloud="block"
		answer = oracle.the_oracle_speaks(question)
		if answer.couplet['artist'].name['name_list'][0] == '':
			artist = answer.couplet['artist'].name['name_list'][1]
		else:
			artist = ' name_part_two '.join(answer.couplet['artist'].name['name_list']).strip()
		og_description="Asked the glitch oracle: '"+question+"' and am told '"+answer.couplet['couplet'][0]+answer.couplet['couplet'][1]+"'"
		page_title="The Glitch Oracle - Psychic Answers from the Infinite Glitch"
		meta_description="Asked the glitch oracle: '"+question+"' and am told '"+answer.couplet['couplet'][0]+answer.couplet['couplet'][1]+"'"
		# TODO: Turn every bit of this info into plain text, then make it possible to share these things.
		og_url="http://www.infiniteglitch.net/share_oracle/"+url_quote_plus(question)+"/"+url_quote_plus(answer.couplet['couplet'][0])+"/"+url_quote_plus(answer.couplet['couplet'][1])+"/"+url_quote_plus(artist)
	else:
		question = answer = ""
		show_cloud = "none"
		page_title="Ask The Glitch Oracle"
		og_description="Ask The Glitch Oracle"
		meta_description="Ask The Glitch Oracle"
		og_url="http://www.infiniteglitch.net/oracle"
	return render_template("oracle.html", page_title="Glitch Oracle", question=question, answer=answer,
							popular_words=popular_words,
							show_cloud=show_cloud, og_description=og_description,
							meta_description=meta_description, og_url=og_url, url_quote_plus=url_quote_plus)

@app.route("/" + apikeys.admin_address)
@admin_required
def admin():
	all_tracks = database.get_many_mp3("all", "sequence, id")
	return render_template("administration.html", all_tracks=all_tracks)

@app.route("/transition/<int:id>")
@admin_required
def manage_transition(id):
	track1 = database.get_single_track(id)
	# Will TypeError if you pick this on the very last one
	track2 = database.next_track_in_sequence(id, track1.track_details['sequence'])
	return render_template("manage_transition.html", track=track1, next_track=track2, url=apikeys.admin_address)

_auditionings = {}
@app.route('/audition', methods=["POST"])
@admin_required
def audition_transition():
	"""Don't know that we need to send the ID through the url"""
	print(request.form)
	id1 = request.form["track_id"]
	id2 = request.form["next_track_id"]
	if "track_hard_transition" in request.form:
		database.update_track(id1, {"otrim":request.form["track_otrim"], "xfade":'-1'})
	else:
	# if track_hard_transition is not checked, override xfade if set to -1
		if database.get_single_track(id1).track_details['xfade'] == -1:
			database.update_track(id1, {"otrim":request.form["track_otrim"], "xfade":0})
		else:
			database.update_track(id1, {"otrim":request.form["track_otrim"]})
	database.update_track(id2, {"itrim":request.form["next_track_itrim"]})
	if len(_auditionings) > 10:
		# Too many concurrent ones. Drop one (chosen arbitrarily).
		_auditionings.popitem()
	token = utils.random_hex()
	_auditionings[token] = subprocess.Popen([sys.executable, "-m", "glitch", "audition", id1, id2, "-", "-ldebug"], stdout=subprocess.PIPE)
	_auditionings[token].output = b""
	return render_template("audition.html",
		track=database.get_single_track(id1),
		next_track=database.get_single_track(id2),
		url=apikeys.admin_address,
		witty_saying="Curiosity has its own reason for existing. -- Aristotle\n\nMainly to keep a lid on the world's population of cats. -- Anonymous",
		trackfn="/audition/%s.mp3" % token,
	)

@app.route("/audition/<token>.mp3")
@admin_required
def hear_transition(token):
	result = _auditionings.get(token)
	if result is None:
		# Bad token (maybe server restarted since this was called for)
		return "Nope", 404
	if isinstance(result, bytes):
		# We have the content, nice. TODO: Clean these out periodically.
		return result
	# Neither of the above? It should be a subprocess object.
	if result.poll() is None:
		# This is a terrible way to prevent deadlocks, but I really don't want
		# tons of threads sitting around. TODO: Make this entire application
		# run under asyncio, like the renderer does. Maybe merge it all in,
		# making the entire server a single asyncio process.
		while result.stdout.peek(): result.output += result.stdout.read(1024)
		return "Not yet", 404
	# It's terminated. Replace it with a string.
	_auditionings[token] = result.output + result.stdout.read()
	return _auditionings[token]

@app.route("/rebuild_glitch")
@admin_required
def rebuild_glitch():
	subprocess.Popen([sys.executable, "-m", "glitch", "major_glitch"], stderr=subprocess.DEVNULL)
	flash("Major Glitch is being rebuilt. No status is available.")
	return redirect("/" + apikeys.admin_address)

@app.route("/delete/<int:id>")
@admin_required
def delete_track_get(id):
	return render_template("delete_track.html", track=database.get_single_track(id), url=apikeys.admin_address)

@app.route("/delete/<int:id>", methods=["POST"])
@admin_required
def delete_track_post(id):
	database.delete_track(id)
	flash("Track %s deleted." % id)
	return redirect("/" + apikeys.admin_address)

@app.route("/edit/<int:id>")
@admin_required
def edit_track_get(id):
	return render_template("track_edit.html", track=database.get_single_track(id))

@app.route("/edit/<int:id>", methods=["POST"])
@admin_required
def edit_track_post(id):
	# TODO: artwork
	database.update_track(id, request.form)
	flash("Track %s edited." % id)
	return redirect("/" + apikeys.admin_address)

# Log 404s to a file, but only once per server start per URL
known_404 = set()
@app.errorhandler(404)
def page_not_found(e):
	if request.path not in known_404:
		known_404.add(request.path)
		with open("404.log", "a") as log:
			print(datetime.datetime.now(), request.path, file=log)
	return render_template('404.html'), 404

# Log 500s to a file, but only once per server start per URL
known_500 = set()
@app.errorhandler(500)
def page_not_found(e):
	if request.path not in known_500:
		known_500.add(request.path)
		with open("500.log", "a") as log:
			print(datetime.datetime.now(), request.path, file=log)
	return render_template('500.html'), 500

# a route for generating sitemap.xml
@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
	"""Generate sitemap.xml. Makes a list of urls and date modified."""
	pages=[]
	ten_days_ago_dt = datetime.datetime.now() - datetime.timedelta(days=10)
	ten_days_ago = ten_days_ago_dt.strftime("%Y-%m-%d")
	# static pages
	for rule in app.url_map.iter_rules():
		if "GET" in rule.methods and len(rule.arguments)==0:
			if (not rule.rule[1:] in [apikeys.admin_address, 'recorder', 'reset_password', 'timing.json', 'rebuild_glitch']):
				pages.append(
					[apikeys.site_url+rule.rule,ten_days_ago]
				)

	for artist in database.all_artists():
		url=url_for("tracks_by_artist",artist=artist[0])
		pages.append([apikeys.site_url+url,ten_days_ago])

	sitemap_xml = render_template('sitemap_template.xml', pages=pages)

	return Response(sitemap_xml, mimetype='text/xml')

@app.route('/google1c870a472b1e6d13.html', methods=['GET'])
def google_verification():
    body = 'google-site-verification: google1c870a472b1e6d13.html'
    return Response(body, mimetype='text/plain')

@app.route('/instrumental_track', methods=['GET'])
def instrumental_track():
	return send_from_directory("static/instrumentals", 'dgacousticlikMP3.mp3', mimetype='audio/mpeg', attachment_filename='glitch_instrumental.mp3', as_attachment=True)

def run(port=config.http_port, disable_logins=False):
	# Used only for debug mode; production mode is done by gunicorn.
	if disable_logins:
		app.config['LOGIN_DISABLED'] = True
	global renderer_port; renderer_port = config.renderer_port
	app.run(host="0.0.0.0", port=port)
