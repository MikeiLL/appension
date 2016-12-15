from . import config
from . import apikeys
from . import server
import sys

dev = 0
if len(sys.argv) > 1:
	dev = 1
import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

server.run(dev) # doesn't return
