import os
import binascii
import hashlib
import functools
import collections
import random
import time
import clize

def random_hex():
	return binascii.b2a_hex(os.urandom(8)).decode("ascii")

def hash_password(password):	
	salt = os.urandom(16)
	hash = hashlib.sha256(salt + password).hexdigest()
	return binascii.hexlify(salt).decode("ascii") + "-" + hash

def check_password(pwd, password):
	if isinstance(pwd, str): pwd = pwd.encode("ascii")
	if isinstance(password, str): password = password.encode("ascii")
	if b"-" not in pwd: return False
	salt, hash = pwd.split(b"-", 1)
	return hashlib.sha256(binascii.unhexlify(salt)+password).hexdigest().encode("ascii") == hash

def alphabetize_ignore_the(list_of_names):
	"""Return alphabetized list of names, ignoring the word "The" in alphabetization.

	TODO: Use a standard locale-based ordering function.
	"""
	
	ordered_object = {}
	#TODO abstract me, please and stop wetting
	for item in list_of_names:
		if item[0][:4].lower() == 'the ':
			ordered_object[item[0][4:].upper()] = ('', item[0])
		elif len(item[0].split(',')) > 1:
			# if item contains a comma, split into Last, First
			the_item = item[0].split(',')
			the_item[1] = the_item[1].lstrip()
			# Add a random number so duplicate names don't break this
			# seems like a bit of a hack. This whole approach is probably
			# less ideal than a really well composed database query.
			# Random names shouldn't be necessary as other two conditions
			# return unique values from the db.
			ordered_object[the_item[0].upper()+str(random.random())] = the_item
		else:
			ordered_object[item[0].upper()] = ('', item[0])
	return collections.OrderedDict(sorted(ordered_object.items()))

# Unless enable_timer() is called, @utils.timeme does nothing.
def timeme(func): return func
def enable_timer():
	global timeme
	def timeme(func):
		"""Decorator to simply and naively profile one function"""
		tm = 0.0
		@functools.wraps(func)
		def wrapper(*a, **kw):
			t = time.time()
			nonlocal tm
			try: return func(*a, **kw)
			finally: tm += time.time() - t
		import atexit
		atexit.register(lambda: print("Total time in %s: %s" % (func.__name__, tm)))
		return wrapper

def systemd_socket():
	"""Look for a socket provided by systemd"""
	try:
		pid = int(os.environ.get("LISTEN_PID", ""))
		fd_count = int(os.environ.get("LISTEN_FDS", ""))
	except ValueError:
		pid = fd_count = 0
	if pid == os.getpid() and fd_count >= 1:
		# The PID matches - we've been given at least one socket.
		# The sd_listen_fds docs say that they should start at FD 3.
		import sys, socket
		print("Got %d socket(s)" % fd_count, file=sys.stderr)
		return socket.socket(fileno=3)
	return None

_commands = []
def cmdline(f):
	# NOTE: functools.wraps, by default, will *replace* the annotations. We want
	# to merge them.
	@functools.wraps(f, assigned=('__name__',), updated=('__dict__', '__annotations__'))
	def wrapper(*a, log:"l"="info", **kw):
		"""
	log: Logging level eg info, debug"""
		import logging
		try: lvl = logging._nameToLevel[log.upper()] # NAUGHTY
		except KeyError: raise clize.ArgumentError("Invalid log level %r" % log)
		logging.basicConfig(level=lvl, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
		return f(*a, **kw)
	# Concatenate the docstrings
	doc = f.__doc__ or f.__name__
	if "\n" not in doc: doc += "\n"
	wrapper.__doc__ = doc + wrapper.__doc__
	_commands.append(wrapper)
	return f
def main():
	clize.run(*_commands, description="Invoke the Infinite Glitch server(s)")
