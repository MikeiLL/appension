from flask import Flask, redirect

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def redirect_all(path):
	return redirect("https://infiniteglitch.net/" + path)

app.run(host="0.0.0.0", port=80)
