import os
import sys
from liveyamlfile import LiveYamlFile


class APIKeys(LiveYamlFile):
	pass

# This is a dirty, dirty hack, but lets you just do:
#   import apikeys
# and have access to an instantiated apikeys object.
apikeys = APIKeys(os.path.join(*(os.path.dirname(__file__).split(os.sep)[:-1] + ['api_keys.yml'])))
# Post our API key into the config for EchoNest
import pyechonest.config
pyechonest.config.ECHO_NEST_API_KEY = apikeys.ECHO_NEST_API_KEY
sys.modules[__name__] = apikeys
