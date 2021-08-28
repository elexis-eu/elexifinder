import csv
import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import lwb
import config


with open(config.datafolder+'newwikibase/fixnorwegian.csv', 'r', encoding="utf-8") as csvfile:
	fixlist = csv.DictReader(csvfile)

	count = 0
	for row in fixlist:
		count +=1
		print('\n['+str(count)+']: ')
		lwb.updateclaim(row['bibitem'],"P11","Q214","item")
