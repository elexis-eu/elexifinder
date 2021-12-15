import sys
import os
import sparql
sys.path.insert(1, os.path.realpath(os.path.pardir))
import lwb
import config

print('Get items that are members of certain classes, and do not have any p42 LexMeta equiv...\n')
query = config.lwb_prefixes+"""

select ?s ?sLabel ?lexmeta ?class

where {

  ?s ldp:P5 lwb:Q7 ; ldp:P5 ?class .
  VALUES ?class {lwb:Q51 lwb:Q50 lwb:Q42 lwb:Q37 lwb:Q35 lwb:Q44 lwb:Q39 lwb:Q52}
  ?s rdfs:label ?sLabel . FILTER (lang(?sLabel)="en")
  filter not exists{?s ldp:P42 ?lexmeta .}
  optional{?s ldp:P74 ?termcoll. filter(?termcoll = lwb:Q49)}

  }
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

	qid = item[0].replace("http://lexbib.elex.is/entity/","")
	lexmeta_interim_uri = item[0]
	lwb.stringclaim(qid, "P42", lexmeta_interim_uri)

# print('Get properties, that do not have any p42 LexMeta equiv...\n')
# query = config.lwb_prefixes+"""
#
# select ?p ?ldp ?pLabel ?lexmeta
#
# where {
#
#   ?p a wikibase:Property ; wikibase:directClaim ?ldp .
#   ?p rdfs:label ?pLabel . FILTER (lang(?pLabel)="en")
#   filter not exists{?p ldp:P42 ?lexmeta .}
#
#   }
