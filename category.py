from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag.stanford import NERTagger
from HTMLParser import HTMLParser
import requests, nltk, json, urllib2, os.path
#nltk.download()
stoplist = stopwords.words("english")
stoplist.append("so")
stoplist.append("tell")
lemmatizer = WordNetLemmatizer()
parser = HTMLParser()
mapfile = 'wordmap.json'
nermuc = NERTagger('stanford-ner/classifiers/english.muc.7class.distsim.crf.ser.gz','stanford-ner/stanford-ner.jar')
nereng = NERTagger('stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz','stanford-ner/stanford-ner.jar')
ner_categories = ['LOCATION', 'TIME', 'PERSON', 'ORGANIZATION', 'MONEY', 'PERCENT', 'DATE']

class WordCategoryChecker:
	def __init__(self, mapfile_batch=10):
		self.mapfile_batch = mapfile_batch
		self.batch_ctr = 0
		if os.path.isfile(mapfile):
			with open(mapfile, 'r') as m_file:
				self.word_map = json.load(m_file)
		else:
			self.word_map = {}

	def store_mapfile(self):
		with open(mapfile,'w') as m_file:
			json.dump(self.word_map,m_file)

	def add_mapping(self, word, category, state):
		if not word in self.word_map:
			self.word_map[word]={}
			self.batch_ctr +=1	
		self.word_map[word][category]=state
		if self.batch_ctr == self.mapfile_batch:
			self.store_mapfile()
			self.batch_ctr = 0

	def check(self, word, category):
		if word == category:
			return True
		word = word.replace(" ","_")		
		if word in self.word_map and category in self.word_map[word]:
			#print "L"
			return self.word_map[word][category]
		else:
			found = False
			if len(word)<100:
				result = requests.get("http://conceptnet5.media.mit.edu/data/5.2/search?limit=1&filter=core&rel=/r/IsA&start=/c/en/"+word+"&end=/c/en/"+category)

				data = result.json()
				
				#print word, len(data['edges'])
				#print data
				for edges in data['edges']:
					#print word, edges
					start = edges['start'].replace("/c/en/","")#.split("_")
					end = edges['end'].replace("/c/en/","")#.split("_")
					weight = float(edges['weight'])
					#print "[",start, end
					if edges['rel'] == '/r/IsA' and word == start and category == end and weight > 2:# and start == word and end == category:
						#print edges
						found = True
						break
				self.add_mapping(word, category, found)	
			return found

class SentenceCategoryChecker:
	def __init__(self, isHTML=False):
		self.word_check = WordCategoryChecker()
		self.isHTML = isHTML

	def check(self, sentence, categories):
		category_list = list(categories)
		orig_sentence = sentence
		result = {}				
		if self.isHTML:
			sentence = nltk.clean_html(parser.unescape(urllib2.unquote(sentence).decode('utf-8', errors='ignore')))
		
		punc_sentence = ''.join(e for e in sentence if e.isalnum() or e.isspace() or e in ['.', ',', '?', '!', "'",':',';','$']) 
		sentence = ''.join(e for e in sentence if e.isalnum() or e.isspace())

		hasNERCateg = False
		for category in category_list:
			result[category] = False
		for categ in ner_categories:
			if categ.lower() in category_list:
				hasNERCateg = True
				category_list.remove(categ.lower())
		if hasNERCateg:			
			result.update(self.get_NER_categ(punc_sentence))
			print "NER", punc_sentence, result
	
		for word in sentence.split(" "):			
			word = lemmatizer.lemmatize(word.lower())
			if not word in stoplist and len(word)>1:				
				#print word
				for category in category_list:					
					if self.word_check.check(word, category):
						result[category] = True
						#print word, category
					else:
						result[category] = False
				#print word
		#print "done"
		result['image'] = self.check_for_image(orig_sentence)	
		return result

	def check_for_image(self, sentence):
		return sentence.find("<img")!= -1

	def get_NER_categ(self, sentence):
		print 'Checking Stanford NER'
		result = {}			
		ner_result = nermuc.tag(sentence.split())		
		for categ in ner_categories:
			if categ in [it[1] for it in ner_result]:
				result[categ.lower()] = True
			else:
				result[categ.lower()] = False
				ner_result = nermuc.tag(sentence.split())		
		ner_result = nereng.tag(sentence.split())
		for categ in ner_categories:
			if categ in [it[1] for it in ner_result]:
				result[categ.lower()] = True

		return result
#sc = SentenceCategoryChecker()
#print sc.check("if there are 2 dogs inside the van, and one got lost. How many dogs would be left?",['car','animal'])
#print sc.check("A sugar cookie recipe calls for 3 1/2 cups of sugar to make 6 dozen cookies. Based on the recipe, how many cups of sugar must be used to make 20 dozen sugar cookies?",['car'])

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
