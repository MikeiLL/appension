# Basic config for stuff that can be easily changed, but which is git-managed.
# See also apikeys_sample.py for the configs which are _not_ git-managed.
app_name = "fore"
server_domain = "http://www.infiniteglitch.net"

lag_limit = 88200        #   samples - how much we can lag by before dropping frames.
restart_timeout = 3      #   seconds between polls to restart.txt
http_port = 8888
mini_http_port = 8193
uid = 1000 # User ID and group ID to drop privileges to
gid = 1000 # Set both to 0 to not drop privileges, eg if the server is started without privs
use_sudo_uid_gid = True # If set, uid/gid will be overridden with SUDO_UID/SUDO_GID if available
frontend_buffer = 20    #   seconds of audio to buffer in frontend
past_played_buffer = 600 #   seconds of audio to store track metadata for in the past
template_dir = "templates/"
drift_limit = 0.1        #   seconds of audio after which drift should be corrected

max_track_length = 400
min_track_length = 90

#   Default values when nothing exists
no_bpm_diff = 20
