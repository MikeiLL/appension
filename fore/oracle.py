"""
Mike iLL 2015

Handle Oracle Question

"""
import string
import random
from stop_words import get_stop_words

stop_words = get_stop_words('en')
stop_words.extend([u'sometimes', u'can', u'will', u'fix', u'just'])

class Couplet(object):
	
	def __init__(self, lyric, couplet):
		couplet = string.capitalize(couplet)
		couplet = couplet.splitlines(True)
		self.couplet = {
					'artist': lyric.track_lyrics['artist'],
					'couplet': couplet,
					'id': lyric.track_lyrics['id']
					}
		
def get_word_list(question):
	question = string.lower(question)
	question = question.translate(string.maketrans("",""), string.punctuation)
	return [word for word in question.split() if word not in stop_words]
	
def compare_to_lyrics(word):
	from fore.database import get_all_lyrics
	track_couplets = []
	all_lyrics = get_all_lyrics()
	for lyric in all_lyrics:
		for couplet in lyric.track_lyrics['couplets']:
			if word in couplet:
				track_couplets.append(Couplet(lyric, couplet))
	if len(track_couplets) > 0:
		return random.choice(track_couplets)
		
def compare_to_keywords(word):
	from fore.database import keyword_lyrics
	track_couplets = []
	matching_lyrics = keyword_lyrics(word)
	for lyric in matching_lyrics:
		for couplet in lyric.track_lyrics['couplets']:
			track_couplets.append(Couplet(lyric, couplet))
	if len(track_couplets) > 0:
		return random.choice(track_couplets)
						 		
def get_random():
	from database import random_lyrics
	lyric = random_lyrics()[0]
	for couplet in lyric.track_lyrics['couplets']:
		return Couplet(lyric, couplet)
		
def the_oracle_speaks(question):
	wordlist = get_word_list(question)
	random.shuffle(wordlist)
	for word in wordlist:
		one = compare_to_lyrics(word)
		if one:
			return one
	for word in wordlist:
		two = compare_to_keywords(word)
		if two:
			return two
	return get_random()
	
		