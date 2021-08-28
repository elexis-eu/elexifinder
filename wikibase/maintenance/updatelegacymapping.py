import sparql
import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import json

query = config.lwb_prefixes+"""
select (strafter(str(?lwburl),"http://lexbib.elex.is/entity/") as ?lwbid) ?legacyID

where {

  ?lwburl ldp:P1 ?legacyID.

  } """

print(query)

url = "https://lexbib.elex.is/query/sparql"
print("Waiting for SPARQL...")
sparqlresults = sparql.query(url,query)
print('\nGot list of items from LexBib SPARQL.')

#go through sparqlresults

rowindex = 0
with open(config.datafolder+"mappings/legacymappings.jsonl", "w", encoding="utf-8") as outfile:
	for row in sparqlresults:
		rowindex += 1
		item = sparql.unpack_row(row, convert=None, convert_type={})
		linejson = {"legacyID":item[1],"lwbid":item[0]}
		outfile.write(json.dumps(linejson)+'\n')
print('Finished.')
