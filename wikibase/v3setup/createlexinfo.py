import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv
import re

with open(config.datafolder+'lexinfo/lexinfo2lwb.csv', 'r', encoding="utf-8") as csvfile:
	terms = csv.DictReader(csvfile)
	count = 0
	for term in terms:
		count += 1
		print('\n['+str(count)+']:')
		enlabel = ""
		otherlabels = {}
		labels = term['labels'].split(";")
		for label in labels:
			labelitem = label.split("@")
			if labelitem[1] == "en":
				enlabel = labelitem[0]
			else:
				otherlabels[labelitem[1]] = labelitem[0]

		termqid = lwb.newitemwithlabel("Q7","en",enlabel)
		collstatement = lwb.itemclaim(termqid,"P74","Q15469")
		for otherlabel in otherlabels:
			lwb.setlabel(termqid,otherlabel,otherlabels[otherlabel])
		externalidstatement = lwb.stringclaim(termqid,"P42",term['s'])
		with open(config.datafolder+'lexinfo/doneitems.csv', "a", encoding="utf-8") as outfile:
			outfile.write(termqid+","+term['s']+'\n')
		print('Item done: '+termqid+": "+term['s']+'\n')
