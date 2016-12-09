from . import config
from . import apikeys
from . import server

import logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')

server.run() # doesn't return
