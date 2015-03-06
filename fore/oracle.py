"""
Mike iLL 2015

Handle Oracle Question

"""
import string
import random
import operator
from stop_words import get_stop_words

stop_words = get_stop_words('en')

'''Why is this happening multiple times?'''
if not u'sometimes' in stop_words:
	stop_words.extend([u'sometimes', u'can', u'will', u'fix', u'just', u'things'])
	
vague_responses = ["hmmm....good question.  not sure i can answer that one.  got another?", 
"i think you're gonna have to answer that for yourself. try another question?", 
"well, if you don't know, i'm certainly not gonna tell you.  try another question?", 
"can you be more specific?", "your question is too vague.  please incude more details.", 
"how in the world would you think i would know about THAT?? Try again with another question.", 
"i want to help, but that's kind of beyond me.  got another question?", 
"wow...no one's ever asked that one before!  i have no idea. is there another question i might be able to help you with?", 
"there are too many ways to answer your question.  can you give me some more details so i can fine tune my response?", 
"is that really so important to you?   is there something else i can help you with?", 
"what do you think the answer is?", 
" i think you should wait and see on that one.  anything else i can help you with?", 
"i'm not so sure you really want to know the answer to that. ask something different."]

class Couplet(object):
	
	def __init__(self, artist, couplet):
		couplet = couplet[:1].upper() + couplet[1:]
		couplet = couplet.splitlines(True)
		self.couplet = {
					'artist': artist,
					'couplet': couplet
					}
		
def get_word_list(question):
	question = string.lower(question)
	question = question.translate(string.maketrans("",""), string.punctuation)
	return [word for word in question.split() if word not in stop_words]
		
def popular_words(wordcount=10):
	from fore.database import get_all_lyrics
	popular = {}
	all_lyrics = get_all_lyrics()
	for lyric in all_lyrics:
		broken_words = [line for line in lyric.track_lyrics['couplets'] for line in line.split()]
		remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
		words_only = [s.translate(remove_punctuation_map) for s in broken_words]

		for word in broken_words:
			if word in popular:
				popular[word] += 1
			else:
				popular[word] = 1
	return popular
						
'''popular_sorted = sorted(popular.iteritems(), key=operator.itemgetter(1), reverse = True)
y = []
for pair in range(10):
	y = y + [popular_sorted[pair][1]]
	print popular_sorted[pair]'''
				 	
def compare_to_lyrics(word):
	from fore.database import match_lyrics
	track_couplets = []
	matching_lyrics = match_lyrics(word)
	for lyric in matching_lyrics:
		for couplet in lyric.track_lyrics['couplets']:
			couplet_copy = couplet
			if word.lower() in couplet_copy.lower():
				track_couplets.append(Couplet(lyric.track_lyrics['artist'], couplet))
	if len(track_couplets) > 0:
		return random.choice(track_couplets)
				
def compare_to_keywords(word):
	from fore.database import match_keywords
	track_couplets = []
	matching_lyrics = match_keywords(word)
	for lyric in matching_lyrics:
		for couplet in lyric.track_lyrics['couplets']:
			track_couplets.append(Couplet(lyric.track_lyrics['artist'], couplet))
	if len(track_couplets) > 0:
		return random.choice(track_couplets)
						 		
def get_random():
	from database import random_lyrics
	lyric = random_lyrics()[0]
	for couplet in lyric.track_lyrics['couplets']:
		return Couplet(lyric.track_lyrics['artist'], couplet)
		
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
	return Couplet("The Glitch Oracle", random.choice(vague_responses) + u'\r ')
	 
	
		
