from . import config
from . import apikeys
from . import server
from . import renderer

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

import sys
if "renderer" in sys.argv:
	renderer.run() # doesn't return
else:
	server.run() # doesn't return
