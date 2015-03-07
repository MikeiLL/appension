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
	
vague_responses = ["Hmmm....good question.  Not sure i can answer that one.  Got another?", 
"I think you're gonna have to answer that for yourself. Try another question?", 
"Well, if you don't know, I'm certainly not gonna tell you.  Try another question?", 
"Can you be more specific?", "Your question is too vague.  Please incude more details.", 
"How in the world would you think I would know about THAT?? Try again with another question.", 
"I want to help, but that's kind of beyond me.  Got another question?", 
"Wow...no one's ever asked that one before!  I have no idea. Is there another question I might be able to help you with?", 
"there are too many ways to answer your question.  can you give me some more details so I can fine tune my response?", 
"Is that really so important to you?  Is there something else i can help you with?", 
"What do you think the answer is?", 
"I think you should wait and see on that one.  Anything else I can help you with?", 
"I'm not so sure you really want to know the answer to that. Ask something different.", 
"The image is foggy. Be brave. Tell me something more intimate.", 
"Excuse me!?! I'm an oracle, not a prophet. Feel free to try again, though.", 
"Meditate on it a little more and try asking again in a different way.", 
"That's a difficult question. Drink something and ask it in a different way.", 
"Goodness gracious. I wish I knew. Ask me something easier.",
"Br$%$%$ttt7&7&8888ixxx$*(@&*&* you're breaking my psychic circuitry. Please ask something easier.",
"Great question! But I fear it's beyond my abilities. Please try something else.",
"I'm seeing a blurry vision of YOU writing a verse about that, friend. What else do you desire knowledge about?",
"The sound of one hand clapping. Ask me something else."]

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
		
def popular_words(wordcount=50):
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
	popular_sorted = sorted(popular.iteritems(), key=operator.itemgetter(1), reverse = True)
	return popular_sorted[:wordcount]
						
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
	 
	
		
