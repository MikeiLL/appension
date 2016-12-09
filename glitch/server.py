from flask import Flask, render_template, g, Markup, request, redirect, url_for, Response
import os
from . import config

app = Flask(__name__)

# Import some stuff from the old package
import fore.assetcompiler
app.jinja_env.globals["compiled"] = fore.assetcompiler.compiled

@app.route("/")
def home():
	return render_template("index.html")

def run():
	if not os.path.isdir("glitch/static/assets"):
		os.mkdir("glitch/static/assets")
	app.run(host="0.0.0.0", port=config.http_port)
