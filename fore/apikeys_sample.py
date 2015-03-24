# Sample untracked-keys file
# If you get errors trying to 'import apikeys', do the following:
# 1) Copy this file to apikeys.py (keeping it in the package directory)
# 2) Replace all of the example values with real ones, particularly the
#    echonest API key
# 3) Generate your own cookie key, possibly using urandom as per below
# Be sure to keep the last two lines as-is.
# You should then be able to start the server.

ECHO_NEST_API_KEY = "BNOAEBT3IZYZI6WXI"
db_connect_string = ""
cookie_monster = "llsfZyohQDa4kRdCCqnoV3gpD8jaHUY0kfkKI3pZlZ4="
# in Python you can generate like this:
# import base64
# import uuid
# print base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
# Thanks to https://gist.github.com/didip/823887
# Alternative way to generate a similar-length nonce:
# import base64, os; print base64.b64encode(os.urandom(33))
system_email = 'server@example.com'
admin_email = 'username@example.com'
# Will use default settings if SMTP_SERVER_PORT == 'localhost'
SMTP_SERVER_PORT = "smtp.gmail.com:587"
SMTP_USERNAME = "email@gmail.com"
SMTP_PASSWORD = "yourpassword"

# HACK: In some cases, the fetching of AudioAnalysis fails. The exact cause is
# currently unknown, but it seems that we can fix the problem by fetching one
# analysis early in the startup process. The fetching MUST be done prior to the
# starting of the mixer, which starts a bunch of processes and threads. I (CJA)
# suspect that there may be an issue with forking and/or threads, but I have no
# idea exactly what's going on here. All I know is that putting a hash in here
# (any existing audio file's hash can be used, I think) seems to fix or mask
# the problem, and the subsequent analysis retrieval always works.
#
# If you don't have problems with AudioAnalysis hanging, don't use this option.
# It slows startup by one entire network round trip - several seconds.
# prime_the_pump = "some md5 hash"

# Keep the below lines as they are.
# Post our API key into the config for EchoNest
import pyechonest.config
pyechonest.config.ECHO_NEST_API_KEY = ECHO_NEST_API_KEY
