import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv
import re

termequivs = {}
broaderrels = {}
with open(config.datafolder+'terms/ContentType_121121.csv', 'r', encoding="utf-8") as csvfile:
	terms = csv.DictReader(csvfile)
	count = 0
	for term in terms:
		count += 1
		print('\n['+str(count)+']...')
		qid = lwb.newitemwithlabel("Q7","en",term['sLabel'])
		collst = lwb.itemclaim(qid,"P74","Q49")
		dmequivst = lwb.stringclaim(qid, "P42",term['s'])
		termequivs[term['s']] = qid
		if len(term['def'])>1:
			defstatement = lwb.stringclaim(qid, "P80", term['def'])
			lwb.setref(defstatement, "P108", term['s'], "url")
		if len(term['broader'])>1:
			broaderrels[qid] = term['broader']

	print('\nNow writing broaderrels...')
	print(str(broaderrels))

	for narrower in broaderrels:
		broaderstatement = lwb.itemclaim(narrower,"P72",termequivs[broaderrels[narrower]])
