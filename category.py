from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import requests
import nltk
#nltk.download()
stoplist = stopwords.words("english")
lemmatizer = WordNetLemmatizer()

class WordCategoryChecker:
	def __init__(self):
		self.word_map = {}

	def add_mapping(self, word, category, state):
		if not word in self.word_map:
			self.word_map[word]={}
		self.word_map[word][category]=state

	def check(self, word, category):
		if word == category:
			return True
		word = word.replace(" ","_")		
		if word in self.word_map and category in self.word_map[word]:
			#print "L"
			return self.word_map[word][category]
		else:			
			result = requests.get("http://conceptnet5.media.mit.edu/data/5.2/search?limit=1&rel=/r/IsA&start=/c/en/"+word+"&end=/c/en/"+category)
			data = result.json()
			found = False
			#print word, len(data['edges'])
			#print data
			for edges in data['edges']:
				#print word, edges
				start = edges['start'].replace("/c/en/","")#.split("_")
				end = edges['end'].replace("/c/en/","")#.split("_")
				#print "[",start, end
				if edges['rel'] == '/r/IsA' and word == start and category == end:# and start == word and end == category:
					#print edges
					found = True
					break
		self.add_mapping(word, category, found)	
		return found

class SentenceCategoryChecker:
	def __init__(self):
		self.word_check = WordCategoryChecker()

	def check(self, sentence, category_list):
		sentence = ''.join(e for e in sentence if e.isalnum() or e.isspace())
		#print sentence 
		result = {}
		for category in category_list:
			result[category]= False
		for word in sentence.split(" "):
			if not word in stoplist:
				word = lemmatizer.lemmatize(word).lower()
				#print word
				for category in category_list:					
					if self.word_check.check(word, category):
						result[category] = True
						#print word, category
				#print word	
		return result

#sc = SentenceCategoryChecker()
#print sc.check("if there are 2 dogs inside the van, and one got lost. How many dogs would be left?",['car','animal'])


'''
cc = CategoryChecker()
print cc.check("cat", "animal")
print "--"
print cc.check("cat", "animal")
print "--"
print cc.check("goose", "animal")
print "--"
print cc.check("horse", "animal")
print cc.check("toyota", "car")
print cc.check("toyota", "animal")
print cc.word_map
'''