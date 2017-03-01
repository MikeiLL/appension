from . import utils

# TODO: Override with port=NNNN if specified by environment

from . import database # Let the database functions register themselves

# Note that these functions lazily import their corresponding modules,
# otherwise package startup would take three parts of forever.

@utils.cmdline
def renderer(*, gain:"g"=0.0):
	"""Invoke the infinite renderer

	gain: dB gain (positive or negative) for volume adjustment
	"""
	from . import renderer
	renderer.run(gain=gain) # doesn't return

@utils.cmdline
def major_glitch(*, dev=False):
	"""Rebuild the Major Glitch"""
	utils.enable_timer()
	from . import renderer
	renderer.major_glitch(profile=dev)

@utils.cmdline
def audition(id1, id2, fn, *, maxlen:"m"=10):
	"""Audition a transition

	id1: ID of earlier track (will render last 10s)

	id2: ID of later track (will render first 10s)

	fn: File name to save into

	maxlen: Approx length of audio either side (0 = all)
	"""
	from . import renderer
	renderer.audition(id1, id2, fn, maxlen=maxlen)

@utils.cmdline
def main(*, dev=False):
	"""Start the main server (debug mode - production uses gunicorn)"""
	from . import server
	server.run(disable_logins=dev) # doesn't return

utils.main()
