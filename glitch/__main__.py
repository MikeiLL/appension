from . import config
from . import apikeys
import argparse

import logging
parser = argparse.ArgumentParser(description="Invoke the Infinite Glitch server(s)")
parser.add_argument("server", help="Server to invoke", choices=["main", "renderer"], nargs="?", default="main")
parser.add_argument("-l", "--log", help="Logging level", type=lambda x: x.upper(),
	choices=logging._nameToLevel, # NAUGHTY
	default="INFO")
arguments = parser.parse_args()
log = logging.getLogger(__name__)
logging.basicConfig(level=getattr(logging, arguments.log), format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

if arguments.server == "renderer":
	from . import renderer
	renderer.run() # doesn't return
else:
	from . import server
	server.run() # doesn't return
