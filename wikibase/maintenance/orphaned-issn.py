import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import lwb
import time
import re

orphaned = ""
print('Will get orphaned ISSN...')
# get issn that are still not linked to an lwb journal ("orphaned issn")

# PREFIX lwb: <http://lexbib.elex.is/entity/>
# PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
#
# select distinct ?issn  where
# { ?s ldp:P5 lwb:Q16; ldp:P20 ?issn .
#  MINUS {?journal ldp:P5 lwb:Q20;
#           ldp:P20 ?issn.}
#
# }

url = "https://lexbib.elex.is/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fqualifier%2F%3E%0A%0Aselect%20distinct%20%3Fissn%20%20where%0A%7B%20%3Fs%20ldp%3AP5%20lwb%3AQ16%3B%20ldp%3AP20%20%3Fissn%20.%0A%20MINUS%20%7B%3Fjournal%20ldp%3AP5%20lwb%3AQ20%3B%0A%20%20%20%20%20%20%20%20%20%20ldp%3AP20%20%3Fissn.%7D%0A%20%20%0A%7D%20"
done = False
while (not done):
	try:
		r = requests.get(url)
		bindings = r.json()['results']['bindings']
	except Exception as ex:
		print('Error: SPARQL request failed: '+str(ex))
		time.sleep(2)
		continue
	done = True
print("Found "+str(len(bindings))+" orphaned ISSN.")

for item in bindings:
	issn = item['issn']['value']
	print('\nNow processing orphaned ISSN '+issn+'...')
	sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent='LexBib-Bibliodata-enrichment-script (lexbib.elex.is)')
	sparql.setQuery('SELECT ?journal ?journalLabel WHERE {?journal wdt:P236 '+'"'+issn+'"'+'. SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}')
	sparql.setReturnFormat(JSON)
	success = 0
	try:
		time.sleep(1.5)
		wddict = sparql.query().convert()
		datalist = wddict['results']['bindings']
		print('\nGot ISSN '+issn+' data from Wikidata.')
		wdqid = datalist[0]['journal']['value'].replace("http://www.wikidata.org/entity/","")
		label = datalist[0]['journalLabel']['value']
		success = 1
		regexp = re.compile(r'Q\d+')
		if regexp.search(label):
			label = ""

	except Exception as ex:
		print("ISSN "+issn+" not found on wikidata, skipping, will add to orphaned list.")
		orphaned += issn+'\tnot found on wikidata.\n'
		continue

	# create lwb serial for this orphaned issn
	lwbqid = lwb.newitemwithlabel("Q20", "en", label) # for serials, wdqid is also lexbib uri
	statement = lwb.stringclaim(lwbqid, "P2", wdqid)
	statement = lwb.stringclaim(lwbqid, "P20", issn)

	# add P46 "part of journal" to bibCollItems with that issn
	# get bibCollItems (class Q16)

	url = "https://lexbib.elex.is/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fdirect%2F%3E%0A%0Aselect%20%3FbibCollItem%20%3Fissn%20%20where%0A%7B%20%3FbibCollItem%20ldp%3AP5%20lwb%3AQ16%20.%0A%20%20%3FbibCollItem%20ldp%3AP20%20%22"+issn+"%22%20.%0A%7D"
	done = False
	while (not done):
		try:
			r2 = requests.get(url)
			bindings2 = r2.json()['results']['bindings']
		except Exception as ex:
			print('Error: SPARQL request failed: '+str(ex))
			time.sleep(2)
			continue
		done = True
	print("\nLooking for BibColl Items with that ISBN, will write P46 links in these items:\n"+str(bindings2))

	for item in bindings2:
		bibCollItem = item['bibCollItem']['value'].replace("http://lexbib.elex.is/entity/","")
		statement = lwb.updateclaim(bibCollItem,"P46",lwbqid,"item")

with open('D:/LexBib/journals/orphaned_issn.txt', 'w', encoding="utf-8") as orphlist:
	orphlist.write(orphaned)

print('Will get orphaned issues...')
# get journal issues with known issn that are still not linked to their journal ("orphaned issue")

# PREFIX lwb: <http://lexbib.elex.is/entity/>
# PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
#
# select ?issue ?issn ?journal where
# { ?issue ldp:P5 lwb:Q16; ldp:P20 ?issn .
#  filter not exists {?issue ldp:P46 ?linked_journal.}
#   ?journal ldp:P5 lwb:Q20; ldp:P20 ?issn.
# }

url = "https://lexbib.elex.is/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fqualifier%2F%3E%0A%0Aselect%20%3Fissue%20%3Fissn%20%3Fjournal%20where%0A%7B%20%3Fissue%20ldp%3AP5%20lwb%3AQ16%3B%20ldp%3AP20%20%3Fissn%20.%0A%20filter%20not%20exists%20%7B%3Fissue%20ldp%3AP46%20%3Flinked_journal.%7D%0A%20%20%3Fjournal%20ldp%3AP5%20lwb%3AQ20%3B%20ldp%3AP20%20%3Fissn.%20%20%0A%7D%20"
done = False
while (not done):
	try:
		r = requests.get(url)
		bindings3 = r.json()['results']['bindings']
	except Exception as ex:
		print('Error: SPARQL request failed: '+str(ex))
		time.sleep(2)
		continue
	done = True
print("Found "+str(len(bindings3))+" orphaned issues.")

for item in bindings3:
	issue = item['issue']['value'].replace("http://lexbib.elex.is/entity/","")
	issn = item['issn']['value']
	journal = item['journal']['value'].replace("http://lexbib.elex.is/entity/","")
	print('\nNow processing orphaned issue '+issue+'...')
	lwb.itemclaim(issue,"P46",journal)
