# Sample untracked-keys file
# If you get errors trying to 'import apikeys', do the following:
# 1) Copy this file to apikeys.py (keeping it in the package directory)
# 2) Replace all of the example values with real ones
# 3) Generate your own cookie key, possibly using urandom as per below
# You should then be able to start the server.

db_connect_string = ""
cookie_monster = "llsfZyohQDa4kRdCCqnoV3gpD8jaHUY0kfkKI3pZlZ4="
# in Python you can generate like this:
# import base64
# import uuid
# print base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
# Thanks to https://gist.github.com/didip/823887
# Alternative way to generate a similar-length nonce:
# import base64, os; print base64.b64encode(os.urandom(33))

# These settings are used only for the sending of emails. The server will
# start with them at the defaults, but all email sending will fail.
system_email = 'server@example.com'
admin_email = 'username@example.com'
# Will use default settings if SMTP_SERVER_PORT == 'localhost'
SMTP_SERVER_PORT = "smtp.gmail.com:587"
SMTP_USERNAME = "email@gmail.com"
SMTP_PASSWORD = "yourpassword"
