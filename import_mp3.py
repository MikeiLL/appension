import argparse
import os.path
from fore import database

parser = argparse.ArgumentParser(description="Bulk-import MP3 files into the appension database",
	epilog="Story, lyrics, and comments will all be blank.")
parser.add_argument("filename", nargs="+", help="MP3 file(s) to import")
parser.add_argument("--submitter", help="Name of submitter", default="Bulk import")
parser.add_argument("--submitteremail", help="Email address of submitter", default="bulk@import.invalid") # or use a real address here
args = parser.parse_args()

# Build up a form-like dictionary for the info mapping. This is the downside of
# the breaching of encapsulation in database.create_track().
info = {"SubmitterName": [args.submitter], "Email": [args.submitteremail]}

for fn in args.filename:
	print("Importing %s"%fn)
	with open(fn, "rb") as f: data = f.read()
	id = database.create_track(data, os.path.split(fn)[-1], info)
	print("Saved as track #%d."%id)
