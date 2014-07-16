from category import WordCategoryChecker
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag.stanford import NERTagger
from HTMLParser import HTMLParser
from multiprocessing import Pool
import ConfigParser, csv, urllib2, nltk, os
import multiprocessing, logging, sys


#Multiprocessing debugger
logger = multiprocessing.log_to_stderr()
logger.setLevel(multiprocessing.SUBDEBUG)
logger.warning('doomed')

parser = HTMLParser()
lemmatizer = WordNetLemmatizer()

# Stop list container
stoplist = stopwords.words("english")
stoplist.append("so")
stoplist.append("tell")

# Conceptnet-based word category checker
word_checker = WordCategoryChecker()

# Category containers
conceptnet_categories = []
NER_categories = []
keyword_categories = {}
columnval_categories = {}

history_file = "history.cfg"

# Named entitory recognizer files
nermuc = NERTagger('stanford-ner/classifiers/english.muc.7class.distsim.crf.ser.gz','stanford-ner/stanford-ner.jar')
nereng = NERTagger('stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz','stanford-ner/stanford-ner.jar')

# Container of word splits in batches
batch_list = None

''' Adds category features to an existing CSV feature-file using ConceptNet, Stanford NER, keywords or column values '''
class DataManager:
	def __init__(self, source_file, output_file, focus_column, read_mode="rU", write_mode="wb", batch = 100, pool_size = 4):
		self.headers = []
		self.source_file = source_file
		self.output_file = output_file
		self.focus_column = focus_column
		self.read_mode = read_mode
		self.write_mode = write_mode
		self.batch = batch
		self.pool_size = pool_size

		self.headers = []
		self.split_pool = None
		self.temp_row = None

		global batch_list
		batch_list = [None] * self.batch

	def process(self):
		self.load_files()
		self.read_data()

	''' Add categories to header for CSV file and store specific category types '''
	def add_header(self, header, header_type = "conceptnet"):
		global conceptnet_categories
		global NER_categories
		global keyword_categories

		if header_type != "keyword" and header_type!= "columnval":
			if not isinstance(header,list):
				header = [header]
			self.headers += header
		if header_type == "conceptnet":
			conceptnet_categories+= header
		elif header_type == "NER":
			NER_categories += header
		elif header_type == "keyword":
			keyword_headers = []
			for topic in header:
				keyword_headers.append(topic[0])
				keyword_categories[topic[0]] = topic[1]
			self.headers += keyword_headers
		elif header_type == "columnval":
			columnval_headers = []
			for columnval in header:
				columnval_headers.append(columnval[0])
				columnval_categories[columnval[0]] = (columnval[1],columnval[2])
			self.headers += columnval_headers


	''' Load source and target files '''
	def load_files(self):
		self.file_reader = csv.reader(open(self.source_file,self.read_mode), delimiter=",")
		self.file_writer = csv.writer(open(self.output_file,self.write_mode), dialect='excel')

	''' Read and process source file then store results to target file '''
	def read_data(self):		
		self.split_pool = Pool(processes=self.pool_size)
		self.temp_row = []
		row_ct = 0

		if self.write_mode == 'a' and os.path.isfile(history_file):
			config = ConfigParser.RawConfigParser()
			config.read(history_file)
			hist_ct = config.getint('History','last_row')
			row_ct = 0
			for i in range(0, hist_ct + 1):
				self.file_reader.next()
				row_ct += 1
		else:
			complete_header = self.file_reader.next() + self.headers
			self.file_writer.writerow(complete_header)

		for row in self.file_reader:
			# Clean, split and store words asynchrously and send results to callback function
			self.split_pool.apply_async(clean_split_store, (row, self.focus_column, row_ct % self.batch), callback = add_result_to_list)

			# Process entire batch				
			if row_ct != 0 and row_ct % self.batch == 0:
				self.process_batch()
				self.store_history(row_ct)
			
			# Append row from source file to temporary containter		
			self.temp_row.append(row)

			print "Row count: "+str(row_ct)
			row_ct += 1

		if (row_ct - 1) % self.batch !=0:
			# Process rows exceeding batch value
			self.process_batch()
			self.store_history(row_ct)

		print "Total read: ", row_ct

	def process_batch(self):
		global batch_list

		# Wait for splitting to finish and reinitialize new Pool				
		self.split_pool.close()
		self.split_pool.join()
		self.split_pool = Pool(processes=self.pool_size)
		
		# Filter array for None values
		batch_list = [x for x in batch_list if x is not None]

		# Get category of each word based on keywords
		process_pool = Pool(processes=self.pool_size)
		keyword_result = process_pool.map_async(get_keyword_categories, batch_list)

		# Get category of each word using conceptnet
		#conceptnet_pool = Pool(processes=self.pool_size)
		conceptnet_result = process_pool.map_async(get_conceptnet_categories, batch_list)

		# Get NER categories
		#NER_pool = Pool(processes=self.pool_size)
		NER_result = process_pool.map_async(get_NER_categories, batch_list)

		# Wait for processes in the batch to finish
		print "Keyword"
		sys.stdout.flush()
		keyword_result = keyword_result.get()
		
		#while(not conceptnet_result.ready()):
		#	print conceptnet_result._number_left
		print "NER"
		sys.stdout.flush()
		NER_result = NER_result.get()

		print "Concept net"
		sys.stdout.flush()
		conceptnet_result = conceptnet_result.get()
		#conceptnet_result = process_pool.map(get_conceptnet_categories, batch_list)
		
		

		# Merge results from each type of category
		for i in range(0,len(keyword_result)):
			keyword_result[i].update(conceptnet_result[i])
			keyword_result[i].update(NER_result[i])
			# Build category values based on values of other columns
			keyword_result[i].update(get_columnval_categories(keyword_result[i]))

		# Build and write column values for CSV file
		for i in range(0,len(self.temp_row)):
			val_row = []
			for column in self.headers:
				val_row.append(keyword_result[i][column])

			cur_row = self.temp_row[i] + val_row
			self.file_writer.writerow(cur_row)

		# Reset temporary containers
		self.temp_row = []
		batch_list = [None] * self.batch

	def store_history(self, last_row):
		config = ConfigParser.RawConfigParser()
		config.add_section('History')
		config.set('History','last_row', last_row)
		with open(history_file, 'w') as f:
			config.write(f)


''' Clean split and return sentence '''
def clean_split_store(data, focus_column, index):
	result = nltk.clean_html(parser.unescape(urllib2.unquote(data[focus_column]).decode('utf-8', errors='ignore'))).split()
	
	# Apply user defined strategies on cleaned and split data
	return (index, result)

''' Add results to list '''
def add_result_to_list(result):
	# [0] - row index
	# [1] - data
	#print "batch adding to ", str(result[0])
	batch_list[result[0]] = result[1]

def get_conceptnet_categories(word_list):
	result = {}
	for category in conceptnet_categories:	
		result[category] = False

	for word in word_list:		
		word = ''.join(e for e in word if e.isalnum() or e.isspace())
		word = lemmatizer.lemmatize(word.lower()) 
		if not word in stoplist and len(word)>1:	
			for category in conceptnet_categories:	
				if word_checker.check(word, category):
					result[category] = True
	return result

def get_keyword_categories(word_list):
	result = {}
	for category in keyword_categories:	
		result[category] = False

	for word in word_list:
		word = ''.join(e for e in word if e.isalnum() or e.isspace())
		if not word in stoplist and len(word)>1:	
			for category in keyword_categories:
				for keyword in keyword_categories[category]:
					if word == keyword:
						result[category] = True
	return result

def get_NER_categories(word_list):
	result = {}			
	for categ in NER_categories:
		result[categ.lower()] = False

	word_list = [''.join(e for e in x if e.isalnum() or e.isspace() or e in ['.', ',', '?', '!', "'",':',';','$']).encode('ascii',errors='ignore') for x in word_list]
	ner_result = nermuc.tag(word_list)		
	for categ in NER_categories:
		if categ in [it[1].lower() for it in ner_result]:
			result[categ.lower()] = True

	ner_result = nereng.tag(word_list)
	for categ in NER_categories:
		if categ in [it[1].lower() for it in ner_result]:
			result[categ.lower()] = True

	return result

def get_columnval_categories(column_results):
	results = {}
	for columnval in columnval_categories:
		func, column_list = columnval_categories[columnval]
		value_list = []
		for column in column_list:
			value_list.append(column_results[column])
		results[columnval] = func(value_list)
	return results
