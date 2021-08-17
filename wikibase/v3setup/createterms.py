# PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
# PREFIX lwb: <http://data.lexbib.org/entity/>
# PREFIX ldp: <http://data.lexbib.org/prop/direct/>
# PREFIX lp: <http://data.lexbib.org/prop/>
# PREFIX lps: <http://data.lexbib.org/prop/statement/>
# PREFIX lpq: <http://data.lexbib.org/prop/qualifier/>
#
# select (strafter(str(?s),"http://data.lexbib.org/entity/") as ?term)
#        (group_concat(distinct concat(str(?sLabel),":",?sLabelLang);SEPARATOR=";") as ?Labels)
#        (group_concat(distinct strafter(str(?v1id),"http://lexbib.org/terms#");SEPARATOR=";") as ?v1ids)
#        (group_concat(distinct strafter(str(?c),"http://data.lexbib.org/entity/");SEPARATOR=";") as ?coll)
#
#   where {
#   ?s ldp:P5 lwb:Q7 ; ldp:P74 ?c .
#   ?s rdfs:label ?sLabel . BIND(str(lang(?sLabel)) as ?sLabelLang)
#   OPTIONAL{?s ldp:P3 ?v1id .}
#   } group by ?s ?Labels ?v1ids ?coll

import config
import lwb
import csv
import re

with open(config.datafolder+'terms/lexbiblegacyterms.csv', 'r', encoding="utf-8") as csvfile:
	terms = csv.DictReader(csvfile)
	count = 0
	for term in terms:
		count += 1
		print('\n['+str(count)+'] Getting v3 term id...')
		qid = lwb.getidfromlegid("Q7", term['term'])
		labels = term['Labels'].split(";")
		labelslist = []
		for label in labels:
			regex = re.search(r'^([^:]+):(.*)', label)
			text=regex.group(1)
			lang=regex.group(2)
			labelslist.append({"lang":lang,"text":text})
			print(str(labelslist))
		for label2write in labelslist:
			lwb.setlabel(qid, label2write['lang'], label2write['text'])
		lwb.updateclaim(qid, "P1", term['term'], "string")
		v1ids = term['v1ids'].split(";")
		for v1id in v1ids:
			if v1id != "":
				lwb.updateclaim(qid,"P106",v1id,"string")
		colls = term['coll'].split(";")
		for v2coll in colls:
			if v2coll != "":
				print("Getting v3 collection...")
				v3coll = lwb.getidfromlegid("Q33", v2coll)
				lwb.updateclaim(qid,"P74",v3coll,"item")
