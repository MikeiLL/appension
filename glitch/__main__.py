from . import config
from . import apikeys
import argparse

# Hack: Allow "python -m glitch database" to be the same as "glitch.database"
import sys
if len(sys.argv) > 1 and sys.argv[1] == "database":
	from . import database
	import clize
	sys.exit(clize.run(*database.commands, args=sys.argv[1:]))

import logging
parser = argparse.ArgumentParser(description="Invoke the Infinite Glitch server(s)")
parser.add_argument("server", help="Server to invoke", choices=["main", "renderer"], nargs="?", default="main")
parser.add_argument("-l", "--log", help="Logging level", type=lambda x: x.upper(),
	choices=logging._nameToLevel, # NAUGHTY
	default="INFO")
parser.add_argument("--dev", help="Dev mode (no logins)", action='store_true')
arguments = parser.parse_args()
log = logging.getLogger(__name__)
logging.basicConfig(level=getattr(logging, arguments.log), format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

if arguments.server == "renderer":
	from . import renderer
	renderer.run() # doesn't return
else:
	from . import server
	server.run(disable_logins=arguments.dev) # doesn't return
