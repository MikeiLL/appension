import sys
import fore.database

if len(sys.argv) > 1:
    track_no = sys.argv[1]
else:
    track_no = 2
analysis = fore.database.get_analysis(track_no)
import pickle, base64
analysis = pickle.loads(base64.b64decode(analysis))
print(analysis)
