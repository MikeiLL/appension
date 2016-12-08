import fore.database
analysis = fore.database.get_analysis(2)
import pickle, base64
analysis = pickle.loads(base64.b64decode(analysis))
print(analysis)
