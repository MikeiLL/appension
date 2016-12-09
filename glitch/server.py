from flask import Flask, render_template, g, Markup, request, redirect, url_for, Response
from . import config

app = Flask(__name__)

@app.route("/")
def home():
	return "Hello, world!"

def run():
	app.run(host="0.0.0.0", port=config.http_port)
