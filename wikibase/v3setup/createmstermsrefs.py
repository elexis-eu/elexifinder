import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv
import re

termequivs = {}
broaderrels = {}
with open(config.datafolder+'terms/ContentType_171121.csv', 'r', encoding="utf-8") as csvfile:
	terms = csv.DictReader(csvfile)
	count = 0
	for term in terms:
		count += 1
		print('\n['+str(count)+']...')
		qid = term['Term']
		collst = term['collst']
		lwb.setref(collst,"P108",term['lexMeta'],"url")
