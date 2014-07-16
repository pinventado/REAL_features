import requests, json, os.path, sys, traceback, urllib2, json

# Debugger for URLLib2
handler=urllib2.HTTPHandler(debuglevel=1)
opener = urllib2.build_opener(handler)
urllib2.install_opener(opener)

mapfile = 'wordmap.json'
s = requests.session()
s.keep_alive = False
''' Retrieves word categories using ConceptNet '''
class WordCategoryChecker:
	def __init__(self, mapfile_batch=10, confidence_threshold = 2):
		self.mapfile_batch = mapfile_batch
		self.batch_ctr = 0
		self.confidence_threshold = confidence_threshold

		if os.path.isfile(mapfile):
			with open(mapfile, 'r') as m_file:
				self.word_map = json.load(m_file)
		else:
			self.word_map = {}

	''' Store dictionary to json file '''
	def store_mapfile(self):
		with open(mapfile,'w') as m_file:
			json.dump(self.word_map,m_file)

	''' Adds a word - category mapping '''
	def add_mapping(self, word, category, state):
		# Create entry if word has not been encountered
		if not word in self.word_map:
			self.word_map[word]={}
			self.batch_ctr +=1
		self.word_map[word][category]=state

		# Store map file when batch value is reached
		if self.batch_ctr == self.mapfile_batch:
			self.store_mapfile()
			self.batch_ctr = 0

	''' Identify if a word belongs to a category '''
	def check(self, word, category):

		# Return if word itself is the category
		if word == category:
			return True

		# Convert " " to "_" according to ConceptNet's standard
		word = word.replace(" ","_")

		# Return category from map file if it has previously been added
		if word in self.word_map and category in self.word_map[word]:
			return self.word_map[word][category]

		# Check if word belongs to a category according to ConceptNet
		else:
			found = False
			# Avoid very long words; they may be other elements like pictures
			if len(word)<100:
				# Send word - category query to ConceptNet
				result = urllib2.urlopen("http://conceptnet5.media.mit.edu/data/5.2/search?limit=1&filter=core&rel=/r/IsA&start=/c/en/"+word+"&end=/c/en/"+category)
				data = json.loads(result.read())

				# Check if ConceptNet results indicate that the word and category are at the start and end of a relationship, it is an "IsA" relationship
				# and the weight (confidence) is acceptable				
				for edges in data['edges']:
					start = edges['start'].replace("/c/en/","")
					end = edges['end'].replace("/c/en/","")
					weight = float(edges['weight'])
					if edges['rel'] == '/r/IsA' and word == start and category == end and weight > self.confidence_threshold:
						found = True
						break
						
				# Add new mapping
				self.add_mapping(word, category, found)	
		return found
		