## assigns term candidates to bibitems. (Term labels are found in English full texts)

import re
import json
import sparql
import json
import requests
import lwb

# load found terms
with open('D:/LexBib/bodytxt/foundterms.json', encoding="utf-8") as infile:
	foundterms = json.load(infile)

#get bibitems to process
query = """
PREFIX lwb: <http://lexbib.elex.is/entity/>
PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
PREFIX lp: <http://lexbib.elex.is/prop/>
PREFIX lps: <http://lexbib.elex.is/prop/statement/>
PREFIX lpq: <http://lexbib.elex.is/prop/qualifier/>

select ?bibItem where
{
  #BIND (lwb:Q9880 as ?bibItem)
  ?bibItem ldp:P5 lwb:Q3 .
  ?bibItem ldp:P11 ?lang .
  filter(?lang = lwb:Q204) # Spanish only
  ?bibItem ldp:P85 ?coll .
  #filter(?coll="1") # coll 1 only

 }
"""
print(query)

url = "https://lexbib.elex.is/query/sparql"
print("Waiting for SPARQL...")
sparqlresults = sparql.query(url,query)
print('\nGot bibItem list from LexBib SPARQL.')

#go through sparqlresults

rowindex = 0
for row in sparqlresults:
	rowindex += 1
	item = sparql.unpack_row(row, convert=None, convert_type={})
	print('\nNow processing item ['+str(rowindex)+']:\n'+str(item))
	bibItem = item[0].replace("http://lexbib.elex.is/entity/","")
	existing = {}
	p96claims = lwb.getclaims(bibItem,"P96")[1]
	if "P96" in p96claims:
		for claim in p96claims["P96"]:
			existing[claim['mainsnak']['datavalue']['value']['id']] = claim['id']

		# writing terms directly to lwb-item
	for termqid in foundterms[bibItem]:
		if foundterms[bibItem][termqid]['hits'] < 3:
			print('This term appears less than three times (skipped): '+termqid)
			continue
		if termqid in existing:
			statement = existing[termqid]
			del existing[termqid]
		else:
			statement = lwb.itemclaim(bibItem, "P96", termqid)
		lwb.setqualifier(bibItem, "P96", statement, "P92", str(foundterms[bibItem][termqid]['hits']), "string")
		#lwb.setqualifier(bibItem, "P96", statement, "P93", str(foundterms[bibItem][termqid]['rfreq']), "string")
	print('There are '+str(len(existing))+' P96 statements for terms that are not (any more) found, will proceed to delete.')
	for garbage in existing:
		lwb.removeclaim(existing[garbage])
