import os
import binascii
import hashlib
import collections
import random
import time

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
		def wrapper(*a, **kw):
			t = time.time()
			nonlocal tm
			try: return func(*a, **kw)
			finally: tm += time.time() - t
		import atexit
		atexit.register(lambda: print("Total time in %s: %s" % (func.__name__, tm)))
		return wrapper
