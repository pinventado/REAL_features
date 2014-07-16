from data import DataManager

import time

# Considers the question a real world value if at least one of the given categories is true
def is_real_world(values):
	return any(values)	

if __name__=="__main__":

	# Source file
	source = "Assistments 12-13 NSF.csv"
	# Output file
	target = "out.csv"

	# Categories to be checked using ConceptNet
	conceptnet_categories = ['car','animal','sport','object','food','subject','place']

	# Categories to be checked using Stanford NER
	NER_categories = ['location','time', 'person', 'organization' ,'money', 'percent','date']

	# Categories based on given keywords
	keyword_categories = [('geometry',['square','circle','rectangle','triangle','angle','quadrant'])]

	# Categories based on values from other columns (limited only to categories in this program)
	columnval_categories = [('real_world_reference',is_real_world,['car','animal','sport','object','food','subject','place','location','person','organization','money'])]

	# Specify column in source data containing questions
	dm = DataManager(source, target, 32, write_mode='a', batch = 100, pool_size = 8)

	# Add categories into header
	dm.add_header(conceptnet_categories,header_type = "conceptnet")
	dm.add_header(NER_categories,header_type = "NER")
	dm.add_header(keyword_categories,header_type = "keyword")
	dm.add_header(columnval_categories,header_type = "columnval")

	# Measure duration of running the program
	start_time = time.time()
	dm.process()
	print time.time() - start_time, "seconds"