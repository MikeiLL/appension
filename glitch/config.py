# Basic config for stuff that can be easily changed, but which is git-managed.
# See also apikeys_sample.py for the configs which are _not_ git-managed.
#server_domain = "http://www.infiniteglitch.net"
server_domain = "http://50.116.55.59"

http_port = 8888 # Port for the main web site, in debug mode
renderer_port = 81 # Port for the renderer (/all.mp3 and friends)

# Track limits in seconds
max_track_length = 400
min_track_length = 90
