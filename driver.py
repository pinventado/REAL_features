from HTMLParser import HTMLParser
from category import SentenceCategoryChecker
import re

def clean_str(str_in):
	str_in = re.sub('<[^>]*>', '', str_in)
	return parser.unescape(str_in)

parser = HTMLParser()
sample = clean_str("<p>Doc Worker is a regular customer at the Waterfront Coffee Shop. The manager has figured that Doc&rsquo;s probability of ordering ham is 0.8; and eggs, 0.65. What is the probability that (leave your answer as a percent, WITHOUT the %)</p><p>e)&nbsp; He orders at least one, either ham or eggs?<strong> </strong></p>")
sc = SentenceCategoryChecker()
categories = ['car','animal']
#print sc.check("if there are 2 dogs inside the van, and one got lost. How many dogs would be left?",['car','animal'])
print sc.check(sample,categories)
