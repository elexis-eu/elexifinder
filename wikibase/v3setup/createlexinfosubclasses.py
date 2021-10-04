import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv
import re
import time

with open(config.datafolder+'lexinfo/doneitems.csv', "r", encoding="utf-8") as donefile:
	donetermitems = donefile.read().split('\n')
	doneterms = {}
	for item in donetermitems:
		if len(item) > 1:
			itempair = item.split(",")
			print(str(itempair))
			doneterms[itempair[1]] = itempair[0]
	print(str(doneterms))



with open(config.datafolder+'lexinfo/lexinfo2lwb.csv', 'r', encoding="utf-8") as csvfile:
	terms = csv.DictReader(csvfile)
	count = 0
	for term in terms:
		count += 1
		print('\n['+str(count)+']:')

		if term['s'] not in doneterms:
			print('Term '+term['s']+' is not in lwb.\n')
			time.sleep(2)
			continue
		termqid = doneterms[term['s']]
		if term['sC'] not in doneterms:
			print('SuperClass'+term['sC']+' is not in lwb.\n')
			time.sleep(2)
			continue
		subClassOf = doneterms[term['sC']]
		broaderstatement = lwb.itemclaim(termqid,"P72",subClassOf)
		if term['comment'] != "":
			defstatement = lwb.stringclaim(termqid,"P80",term['comment'])
			lwb.setref(defstatement, "P108", term['s'], "url")



		print('Item done: '+termqid+": "+term['s']+'\n')
