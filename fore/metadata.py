import colors
import apikeys
import logging
import cStringIO
import traceback

PIXELS_PER_SECOND = 1

log = logging.getLogger(__name__)


def Metadata(x):
	"""Neutered Metadata class"""
	return x