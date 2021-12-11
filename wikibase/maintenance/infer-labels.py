import time
import re
import json
import csv
from collections import OrderedDict
from datetime import datetime
import sys
import os
import sparql
import json
sys.path.insert(1, os.path.realpath(os.path.pardir))
import lwb
import config

print('Get items that infer labels from other items (P149)...\n')
query = config.lwb_prefixes+"""

select

  ?uri
  ?labelsource
 (concat('[ ',(group_concat(distinct concat('{"',lang(?preflabel),'": "',?preflabel,'"}');SEPARATOR=", ")),' ]') as ?preflabels)
 (concat('[ ',(group_concat(distinct concat('{"',lang(?altlabel),'": "',?altlabel,'"}');SEPARATOR=", ")),' ]') as ?altlabels)
 ?wd


 where {

  ?uri ldp:P149 ?labelsource .
  ?labelsource rdfs:label ?preflabel ;

  OPTIONAL { ?labelsource skos:altLabel ?altlabel. }

   OPTIONAL { ?uri ldp:P2 ?wd.}


} GROUP BY ?uri ?labelsource ?preflabels ?altlabels ?wd
"""
#print(query)

url = "https://lexbib.elex.is/query/sparql"
print("Waiting for SPARQL...")
sparqlresults = sparql.query(url,query)
print('\nGot list from LexBib SPARQL.')

#go through sparqlresults
rowindex = 0

for row in sparqlresults:
	rowindex += 1
	item = sparql.unpack_row(row, convert=None, convert_type={})
	print('\nNow processing item ['+str(rowindex)+']...')
	#print(str(item))

	target = item[0].replace("http://lexbib.elex.is/entity/","")
	source = item[1].replace("http://lexbib.elex.is/entity/","")

	# prefLabels
	for entry in json.loads(item[2]):
		lang = list(entry.keys())[0]
		lwb.setlabel(target, lang, entry[lang])

	# altLabels
	if item[3]:
		altLabels = {}
		for entry in json.loads(item[3]):
			lang = list(entry.keys())[0]
			if lang not in altLabels:
				altLabels[lang] = []
			altLabels[lang].append(entry[lang])

		for labellang in altLabels:
			aliasstring = ""
			for label in altLabels[labellang]:
				aliasstring += "|"+label
			lwb.setlabel(target, lang, aliasstring[1:], type="alias", set=True)
