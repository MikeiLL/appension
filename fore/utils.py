#!/usr/bin/env python
# encoding: utf-8
"""
utils.py

Created by Jason Sundram, on 2010-04-05.
Copyright (c) 2010 The Echo Nest. All rights reserved.
"""

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

magic_log = open("magic.log", "w")

class Magic_Str(str):
	"""Callable string. If called, it returns itself with () appended.
	It's also able to be treated as an integer (it'll be zero).
	"""
	def __call__(self, *args, **kw):
		print >>magic_log, self+"()"
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
	def __repr__(self):
		return "Magic_Anything(" + repr(self._id) + ")"
	def __getattribute__(self, name):
		if name == "id": return self._id
		if name.startswith("_"): return object.__getattribute__(self, name)
		print >>magic_log, repr(self) + "." + name
		return Magic_Str(repr(self) + "." + name)
