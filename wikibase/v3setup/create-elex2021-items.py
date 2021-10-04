import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv
import json

timeobj = {'time':"+2021-07-07T00:00:00Z",'precision':10}

with open('D:/Lab_LexBib/elex-2021/procs_parsed.jsonl', 'r', encoding="utf-8") as jsonlfile:
	items = jsonlfile.read().split('\n')
	bibitems = []
	for item in items:
		if len(item) > 1:
			print(item)
			bibitems.append(json.loads(item))
	print(str(bibitems))

	count = 0
	for bibitem in bibitems:
		bibitemqid = lwb.newitemwithlabel("Q3","en",bibitem['title'])
		typestatement = lwb.updateclaim(bibitemqid,"P100","Q27","item")
		titlestatement = lwb.updateclaim(bibitemqid,"P6",{"language":"en","text":bibitem['title']},"monolingualtext")
		listpos = 0
		for author in bibitem['authors']:
			listpos += 1
			authorstatement = lwb.updateclaim(bibitemqid,"P12",author,"novalue")
			lwb.setqualifier(bibitemqid,"P12",authorstatement,"P33",str(listpos),"string")
			lwb.setqualifier(bibitemqid,"P12",authorstatement,"P38",author,"string")
		eventstatement = lwb.updateclaim(bibitemqid,"P36","Q15736","item")
		timestatement = lwb.updateclaim(bibitemqid,"P15",timeobj,"time")
		pdfstatement = lwb.updateclaim(bibitemqid,"P21",bibitem['pdf'],"url")
		pagesstatement = lwb.updateclaim(bibitemqid,"P24",bibitem['pages'],"url")
