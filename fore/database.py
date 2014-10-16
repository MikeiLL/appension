import apikeys
import psycopg2

_conn = psycopg2.connect(apikeys.db_connect_string)

def get_mp3(some_specifier):
	with _conn.cursor():
		# TODO: Fetch an MP3 and return its raw data
		pass

def get_many_mp3():
	with _conn.cursor():
		# TODO: Enumerate a bunch of MP3s and return their identifiers
		pass


# Etcetera.
