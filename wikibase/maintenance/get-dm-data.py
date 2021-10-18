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

classes_to_update = ["Q8"]

with open(config.datafolder+"ontology/DM_sources_defs.csv", "r", encoding="utf-8") as sourcecsv:
	dmcsv = csv.DictReader(sourcecsv, delimiter=",")

	dm = {}
	for line in dmcsv:
		dm[line['s']] = {'scopenote':line['scopenote'],'comment':line['comment'],'rdftype':line['rdftype'],'subclassof':line['subclassof']}



# Get LWB items belonging to class c that have P2 (wdid) set
query = """PREFIX lwb: <http://lexbib.elex.is/entity/>
PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
select ?item ?dmequiv where
{ ?item ldp:P42 ?dmequiv.
  filter not exists{?item ldp:P80 ?def.}}"""
print("Waiting for LexBib v3 SPARQL (load DM-equivs (P42))...")
sparqlresults = sparql.query('https://lexbib.elex.is/query/sparql',query)
print('Got data from LexBib v3 SPARQL.')
#go through sparqlresults
#classmembers = []
for row in sparqlresults:
	sparqlitem = sparql.unpack_row(row, convert=None, convert_type={})
	print('\nNow processing:\n'+str(sparqlitem))
	lwbqid = sparqlitem[0].replace("http://lexbib.elex.is/entity/","")
	dm_equiv = sparqlitem[1]
	if dm_equiv in dm:
		print('Found data for dm-entity '+dm_equiv)
		print(str(dm[dm_equiv]))
		desc = None
		if dm[dm_equiv]['scopenote'] != "":
			desc = dm[dm_equiv]['scopenote']
		elif dm[dm_equiv]['comment'] != "":
			desc = dm[dm_equiv]['comment']
		if desc:
			statement = lwb.updateclaim(lwbqid,"P80",desc,"string")
			lwb.setref(statement, "P108", dm_equiv, "url")
