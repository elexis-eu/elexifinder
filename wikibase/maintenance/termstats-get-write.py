import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv
import re
import time
import json

corpname = "LexBib EN/ES Dic 2021"

query = """
PREFIX lwb: <http://lexbib.elex.is/entity/>
PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
PREFIX lp: <http://lexbib.elex.is/prop/>
PREFIX lps: <http://lexbib.elex.is/prop/statement/>
PREFIX lpq: <http://lexbib.elex.is/prop/qualifier/>
PREFIX lpr: <http://lexbib.elex.is/prop/reference/>
PREFIX lno: <http://lexbib.elex.is/prop/novalue/>

select ?sLabel (group_concat(distinct strafter(str(?s),"http://lexbib.elex.is/entity/");SEPARATOR=";") as ?uris) (count(?s) as ?count) where {

 ?facet ldp:P131 lwb:Q1.
  ?s ldp:P5 lwb:Q7.
  ?s ldp:P72+ ?facet.

  ?s rdfs:label|skos:altLabel ?sLabel . FILTER (lang(?sLabel)="""+wikilang+""")

}  group by ?sLabel ?uri ?count
order by desc(?count)

"""
print(query)

url = "https://lexbib.elex.is/query/sparql"
print("Waiting for SPARQL... Getting term stats..."+isolang)
sparqlresults = sparql.query(url,query)
print('\nGot it.')

#go through sparqlresults
rowindex = 0

for row in sparqlresults:
	rowindex += 1
	item = sparql.unpack_row(row, convert=None, convert_type={})
	termqid = item[0].replace("http://lexbib.elex.is/entity/","")
	print('\nNow processing ['+str(count)+'] '+termqid+'.')
	found_in_articles = item[1]

	existingstatements = lwb.getclaims(termqid,"P109")[1]
	#print('existingcreators: '+str(existingcreators))
	hits_statement = None
	p84quali = None
	if existingstatements and ("P109" in existingstatements):
		for existingstatement in existingstatements["P109"]:
			if existingstatement['mainsnak']['datavalue']['value'] == found_in_articles:
				hits_statement = existingstatement['id']
				if "qualifiers" in existingstatement and "P84" in existingstatement['qualifiers']:
					for sourceclaim in existingstatement['qualifiers']["P84"]:
						if sourceclaim['datavalue']['value'] == corpname:
							print('Found redundant p84 quali, skipped.')
							p84quali = True
				break
	if not hits_statement:
		hits_statement = lwb.stringclaim(termqid,"P109",str(found_in_articles)
	if not p84quali:
		lwb.setqualifier(termqid, "P109", hits_statement, "P84", corpname, "string")
