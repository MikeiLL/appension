# Basic config for stuff that can be easily changed, but which is git-managed.
# See also apikeys_sample.py for the configs which are _not_ git-managed.
server_domain = "http://www.infiniteglitch.net"

http_port = 8888
uid = 0 # User ID and group ID to drop privileges to
gid = 0 # Set both to 0 to not drop privileges, eg if the server is started without privs
use_sudo_uid_gid = True # If set, uid/gid will be overridden with SUDO_UID/SUDO_GID if available

# Track limits in seconds
max_track_length = 400
min_track_length = 90
