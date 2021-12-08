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

print('(1) get broader-related concepts where the inverse narrow relation is not present...\n')
query = config.lwb_prefixes+"""
PREFIX owl: <http://www.w3.org/2002/07/owl#>
select distinct ?n ?nLabel ?b ?bLabel (REPLACE(STR(?redirect),".*Q","Q") AS ?redirect_qid)

where {

  ?n ldp:P5 lwb:Q7.
  ?n rdfs:label ?nLabel . FILTER (lang(?nLabel)="en")
  ?n ldp:P72 ?b.
 # ?n lp:P72 ?bs .
 # ?bs lps:P72 ?b .
  {?b ldp:P5 lwb:Q7 ;
  rdfs:label ?bLabel . filter (lang(?bLabel)="en")}
  UNION
  {?b owl:sameAs ?redirect.}

  filter not exists { ?b ldp:P73 ?n . }


#  {?redirect rdfs:label ?rLabel .}UNION {?b rdfs:label ?rLabel .}FILTER (lang(?rLabel)="en")
  }
"""
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
	print('\nNow processing item ['+str(rowindex)+']...')
	print(str(item))
	narrower_uri = item[0].replace("http://lexbib.elex.is/entity/","")
	narrower_label = item[1]
	broader_uri = item[2].replace("http://lexbib.elex.is/entity/","")
	broader_label = item[3]
	redirect_qid = item[4]
	if redirect_qid != None: # broader-rel points to redirect item
		if redirect_qid.startswith("Q"):
			print('Updating '+broader_uri+' redirect with '+redirect_qid+'...')
			broaderclaims = lwb.getclaims(narrower_uri,"P72")[1]
			if "P72" in broaderclaims:
				broaderstatement = broaderclaims['P72'][0]['id']
				lwb.setclaimvalue(broaderstatement, redirect_qid, "item")
				print('Updating relation: '+narrower_uri+' "'+str(broader_label)+'" (skos:narrower) "'+str(narrower_label)+'"...')
				lwb.updateclaim(redirect_qid,"P73",narrower_uri,"item")
		else:
			print('Strange: for '+broader_uri+' I got redirect: '+redirect_qid)
	else:
		print('Updating relation: '+narrower_uri+' "'+broader_label+'" (skos:narrower) "'+narrower_label+'"...')
		lwb.updateclaim(broader_uri,"P73",narrower_uri,"item")


print('\n\n________________________________________________________\n\n(2) get orphaned narrower relations (where the broader has been removed)...\n')
query = config.lwb_prefixes+"""

select distinct ?n ?nLabel ?narstatement ?b ?bLabel

where {

  ?n ldp:P5 lwb:Q7.
  ?n rdfs:label ?nLabel . FILTER (lang(?nLabel)="en")
  ?b lp:P73 ?narstatement .
  ?narstatement lps:P73 ?n .
  filter not exists { ?n ldp:P72 ?b . }

  ?b rdfs:label ?bLabel . FILTER (lang(?bLabel)="en")

  }
"""
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
	print('\nNow processing item ['+str(rowindex)+']\n')
	narrower_uri = item[0].replace("http://lexbib.elex.is/entity/","")
	narrower_label = item[1]
	narstatement = item[2].replace("http://lexbib.elex.is/entity/statement/","")
	broader_uri = item[3].replace("http://lexbib.elex.is/entity/","")
	broader_label = item[4]
	print('Removing orphaned narrower-rel: "'+broader_label+'" (skos:narrower) "'+narrower_label+'"...')
	lwb.removeclaim(narstatement)
