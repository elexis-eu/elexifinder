from SPARQLWrapper import SPARQLWrapper, JSON
import time
import sys
import json
import requests
import mwclient
import sparql
import csv
import os
import sys
sys.path.insert(1, os.path.realpath(os.path.pardir))
import lwb
import config

print('\nWill get dictionary distributions and any existing P55 link pointing to them.')
query = """PREFIX lwb: <http://lexbib.elex.is/entity/>
PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
PREFIX lp: <http://lexbib.elex.is/prop/>
PREFIX lps: <http://lexbib.elex.is/prop/statement/>
PREFIX lpq: <http://lexbib.elex.is/prop/qualifier/>
PREFIX lpr: <http://lexbib.elex.is/prop/reference/>

select ?uri ?date ?title ?lcr where
{ ?uri ldp:P5 lwb:Q24; # Q24: Dictionary Distribution
 OPTIONAL { ?lcr ldp:P55 ?uri .}
 OPTIONAL { ?uri ldp:P6 ?title;
                 ldp:P15 ?date. }


} group by ?uri ?date ?title ?lcr
"""
print("Waiting for LexBib v3 SPARQL...")
sparqlresults = sparql.query('https://lexbib.elex.is/query/sparql',query)
print('Got data from LexBib v3 SPARQL.')
#go through sparqlresults

for row in sparqlresults:
	item = sparql.unpack_row(row, convert=None, convert_type={})
	distrqid = item[0].replace('http://lexbib.elex.is/entity/','')
	date = item[1]
	title = item[2]
	print('\nNow processing:',distrqid,date,title)
	if item[3]:
		lcrqid = item[3].replace('http://lexbib.elex.is/entity/','')
		print('Found P55 link for this dictionary distribution. LCR is '+lcrqid)
	else:
		print('No P55 link for this dictionary distribution. Will create a new Q4 item.')
		lcrqid = lwb.newitemwithlabel("Q4","en",title)
	linkstatement = lwb.updateclaim(lcrqid,"P55",distrqid,"item")
	dateclaim = lwb.setqualifier(lcrqid,"P55",linkstatement,"P126",str(date)[0:4],"string")
