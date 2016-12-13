#!/usr/bin/env python
from __future__ import print_function
"""
utils.py

Created by Jason Sundram, on 2010-04-05.
Copyright (c) 2010 The Echo Nest. All rights reserved.
Expanded Chris Angelico 2014 with additional utilities.
"""
import threading, os
import binascii
import hashlib
import collections

def flatten(l):
	""" Converts a list of tuples to a flat list.
		e.g. flatten([(1,2), (3,4)]) => [1,2,3,4]
	"""
	return [item for pair in l for item in pair]

def tuples(l, n=2):
	""" returns n-tuples from l.
		e.g. tuples(range(4), n=2) -> [(0, 1), (1, 2), (2, 3)]
	"""
	return zip(*[l[i:] for i in range(n)])

def rows(m):
	"""returns the # of rows in a numpy matrix"""
	return m.shape[0]

magic_log = None

class Magic_Str(str):
	"""Callable string. If called, it returns itself with () appended.
	It's also able to be treated as an integer (it'll be zero).
	"""
	def __call__(self, *args, **kw):
		print(self+"()", file=magic_log); magic_log.flush()
		return self+"()"
	def __int__(self): return 0
	def __index__(self): return 0

class Magic_Anything(object):
	"""
	Magic class that has every possible method/attribute
	
	Actually, there are no methods, per se. When any attribute is sought,
	a Magic_Str() will be returned.
	"""
	def __init__(self, id):
		self._id = id
		if not magic_log: magic_log = open("magic.log", "w")
	def __repr__(self):
		return "Magic_Anything(" + repr(self._id) + ")"
	def __getattribute__(self, name):
		if name == "id": return self._id
		if name.startswith("_"): return object.__getattribute__(self, name)
		print(repr(self) + "." + name, file=magic_log); magic_log.flush()
		return Magic_Str(repr(self) + "." + name)

def shuffler(func, gen):
	"""Call func(next(gen)) repeatedly.

	TODO: Should this become for x in gen: func(x) ?
	Currently, a StopIteration will bubble unexpectedly.

	Not currently used.
	"""
	while True:
		func(next(gen))

def daemonize(target, *args):
	"""Start a daemon thread to call target(*args)."""
	t = threading.Thread(target=target, args=args)
	t.daemon = True
	t.start()
	
def random_hex():
	return binascii.b2a_hex(os.urandom(8)).decode("ascii")

def hash_password(password):	
	salt = os.urandom(16)
	hash = hashlib.sha256(salt + password).hexdigest()
	return binascii.hexlify(salt).decode("ascii") + "-" + hash

def check_password(pwd, password):
	if "-" not in pwd: return False
	salt, hash = pwd.split("-", 1)
	return hashlib.sha256(salt.decode("hex")+password).hexdigest() == hash

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
