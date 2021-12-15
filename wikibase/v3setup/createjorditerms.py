import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv
import re

with open(config.datafolder+'terms/jordi_porta.csv', 'r', encoding="utf-8") as csvfile:
	terms = csv.DictReader(csvfile)
	count = 0
	for term in terms:
		count += 1
		print('\n['+str(count)+']...')
		qid = term['concepturi']
		prefLabel = term['termEsLabel']
		lwb.setlabel(qid, "es", prefLabel)
		prefLabelStatement = lwb.updateclaim(qid, "P129", {'language':'es','text':prefLabel}, "monolingualtext")
		lwb.setqualifier(qid,"P129",prefLabelStatement,"P128","COMPLETED","string")

		altLabelList = []
		altLabels = term['EsAltLabels'].split("|")
		for altLabel in altLabels:
			if len(altLabel) > 1 and altLabel not in altLabelList:
				altLabelList.append(altLabel)
		aliasstring = "|".join(altLabelList)
		lwb.setlabel(qid,"es",aliasstring,type="alias",set=True)
		for alias in altLabelList:
			altLabelStatement = lwb.updateclaim(qid, "P130", {'language':'es','text':altLabel}, "monolingualtext")
			lwb.setqualifier(qid,"P129",altLabelStatement,"P128","COMPLETED","string")
