from . import utils

# TODO: Override with port=NNNN if specified by environment

@utils.cmdline
def renderer():
	"""Invoke the infinite renderer"""
	from . import renderer
	renderer.run() # doesn't return

@utils.cmdline
def major_glitch(*, dev=False):
	"""Rebuild the Major Glitch"""
	utils.enable_timer()
	from . import renderer
	renderer.major_glitch(profile=dev)

@utils.cmdline
def audition(id1, id2, fn):
	"""Audition a transition"""
	from . import renderer
	renderer.audition(id1, id2, fn)

@utils.cmdline
def main(*, dev=False):
	"""Start the main server (debug mode - production uses gunicorn)"""
	from . import server
	server.run(disable_logins=dev) # doesn't return

utils.main()
