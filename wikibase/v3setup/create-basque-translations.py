import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv
import json

with open('D:/LexBib/LexVoc/LexVoc_Basque.csv', 'r', encoding="utf-8") as csvfile:
	rows = csv.DictReader(csvfile)

	count = 0
	for row in rows:
		count += 1
		termqid = row['subject'].replace("http://lexbib.elex.is/entity/","")
		print('\n['+str(count)+'] Now processing term '+termqid+'...')
		prefLabel = row['euPrefLabel']
		altLabels = row['euAltLabels']

		lwb.setlabel(termqid,"eu",prefLabel.strip(),type="label")
		prefLabelStatement = lwb.updateclaim(termqid,"P129",{'language':"eu",'text':prefLabel.strip()},"monolingualtext")
		lwb.setqualifier(termqid,"P129",prefLabelStatement,"P128","COMPLETED","string")
		if altLabels != "":
			lwb.setlabel(termqid,"eu",altLabels,type="alias",set=True)
			altLabelList = altLabels.replace("|","@").split("@")
			for altLabel in altLabelList:
				altLabelStatement = lwb.updateclaim(termqid,"P130",{'language':"eu",'text':altLabel},"monolingualtext")
				lwb.setqualifier(termqid,"P129",altLabelStatement,"P128","COMPLETED","string")
