import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import time
import json
import requests
import csv
import lwb # functions for data.lexbib.org (LWB: LexBib WikiBase) I/O operations
import config
import langmapping
import sparql

print ('This is to copy multilingual labels from wikidata, for the following languages:')

allowed_languages = []
for iso3lang in langmapping.langcodemapping: # gets LexVoc elexis languages
	allowed_languages.append(langmapping.getWikiLangCode(iso3lang))
print(str(allowed_languages))

# done_items = []


query = config.lwb_prefixes+"""
select (strafter(str(?lang),"http://lexbib.elex.is/entity/") as ?lwb) ?wd

where {
  ?lang ldp:P5 lwb:Q8;
        ldp:P2 ?wd .

  filter not exists{?lang rdfs:label ?label. filter(lang(?label) != "en")}

  }"""

print(query)

url = "https://lexbib.elex.is/query/sparql"
print("Waiting for SPARQL...")
sparqlresults = sparql.query(url,query)
print('\nGot term list from LexBib SPARQL.')

#go through sparqlresults
rowindex = 0

for row in sparqlresults:
	rowindex += 1
	item = sparql.unpack_row(row, convert=None, convert_type={})
	lwbqid = item[0]
	wdqid = item[1]
	# if lwbqid in done_items:
	# 	print('\nItem ['+str(rowindex)+'] has been done in a previous run.')
	# 	continue
	print('\nItem ['+str(rowindex)+']:')
	print('Will now get labels for LWB item: '+lwbqid+' from wdItem: '+wdqid)
	done = False
	while (not done):
		try:
			r = requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=labels&ids="+wdqid).json()
			#print(str(r))
			if "labels" in r['entities'][wdqid]:
				for labellang in r['entities'][wdqid]['labels']:
					if labellang in allowed_languages:
						value = r['entities'][wdqid]['labels'][labellang]['value']

						lwb.setlabel(lwbqid,labellang,value)

						#existinglabel = lwb.getlabel(lwbqid,labellang)

						# if not existinglabel:
						# 	lwb.setlabel(lwbqid,labellang,value)
						# else:
						# 	if existinglabel.lower() != value.lower():
						# 		lwb.setlabel(lwbqid,labellang,value, type="alias")
				done = True

		except Exception as ex:
			print('Wikidata: Label copy operation failed, will try again...\n'+str(ex))
			time.sleep(4)

	# with open(config.datafolder+'terms/terms_wdqids_done.txt', 'a') as outfile:
	# 	outfile.write(lwbqid+'\n')
