from category import SentenceCategoryChecker
import re, csv, nltk

'''def clean_str(str_in):
	str_in = re.sub('<[^>]*>', '', str_in)
	return parser.unescape(str_in)
'''
#sample = clean_str("<p>Doc Worker is a regular customer at the Waterfront Coffee Shop. The manager has figured that Doc&rsquo;s probability of ordering ham is 0.8; and eggs, 0.65. What is the probability that (leave your answer as a percent, WITHOUT the %)</p><p>e)&nbsp; He orders at least one, either ham or eggs?<strong> </strong></p>")
sc = SentenceCategoryChecker(isHTML=True)
#categories = ['car','animal']
categories = ['car','animal','person','sport','place','object','food','subject']
header = ["Question"]
#line = "Question, "
#first = True   
for categ in categories:
	header.append(categ)
#print header
#		out = categ
#		if first:
#			first = False
#		else:
#			out = ", "+categ 
#		line += out 
#print line

#with open("temp.csv","r") as f:
#	data = f.readlines()

csv_file = open("temp.csv","rU")
out_file = open("out.csv","wb")
reader = csv.reader(csv_file, delimiter=",")
writer = csv.writer(out_file, dialect='excel')
writer.writerow(header)
for row in reader:
	if len(row)>0:
		cur_row = [row[0]]
		#print cur_row
		#sample = row[0]
		#line = sample+","
		'''line = '"'+nltk.clean_html(sample)+'", '
		if line.strip() == '':
			break'''
		#first = True
		results = sc.check(row[0], categories)
		for item in categories:
			cur_row.append(results[item])
			#out = str(col[1])
			#if first:
			#	first = False
			#else:
			#	out = ", "+str(col[1])
			#line+= out
			#print item 		
			#cur_row.append(col[1])
		print cur_row
		writer.writerow(cur_row)
	
#print sc.check("if there are 2 dogs inside the van, and one got lost. How many dogs would be left?",['car','animal'])
'''ctr = 0
with open('temp.csv','r') as f:
	entry = f.readlines()
	#print entry
	ctr+=1
	print sc.check(entry,categories)
'''