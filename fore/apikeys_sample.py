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
admin_url = "/123administration45"
delete_url = "/x1x2x3x4x5"
edit_url = "/hard_to_guess"
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

# Keep the below lines as they are.
# Post our API key into the config for EchoNest
import pyechonest.config
pyechonest.config.ECHO_NEST_API_KEY = ECHO_NEST_API_KEY