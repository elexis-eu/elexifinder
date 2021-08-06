import sparql
import config
import json

query = config.lwb_prefixes+"""
select (strafter(str(?lwburl),"http://lexbib.elex.is/entity/") as ?lwbid) ?wppage

where {

  ?lwburl ldp:P66 ?wppage.
  BIND(xsd:integer(strafter(str(?lwburl),"http://lexbib.elex.is/entity/Q")) as ?order)

  } ORDER BY ?order"""

print(query)

url = "https://lexbib.elex.is/query/sparql"
print("Waiting for SPARQL...")
sparqlresults = sparql.query(url,query)
print('\nGot list of items from LexBib SPARQL.')

#go through sparqlresults

rowindex = 0
with open(config.datafolder+"mappings/wppage_lwbplace.jsonl", "w", encoding="utf-8") as outfile:
	for row in sparqlresults:
		rowindex += 1
		item = sparql.unpack_row(row, convert=None, convert_type={})
		linejson = {"lwbid":item[0],"wppage":item[1]}
		outfile.write(json.dumps(linejson)+'\n')
print('Finished.')
