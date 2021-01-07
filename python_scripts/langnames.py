

from datetime import datetime
import sys
import re
import os
import requests
import wget
from w3lib.html import replace_entities
import json
import csv
import shutil
from SPARQLWrapper import SPARQLWrapper, JSON
import time
from rdflib import Graph, Namespace, BNode, URIRef, Literal


#query wikidata
sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent='LexBib-Bibliodata-enrichment-script (lexbib.org)')
sparql.setQuery("""SELECT ?isocode ?lang ?langName (lang(?langName) as ?langNamelang)
                WHERE
                    {
                    ?lang wdt:P220 ?isocode .
                    ?lang rdfs:label ?langName .
                    filter regex(str(lang(?langName)) , "^en|^de|^es|^eu|^ca|^gl|^sl|^fr|^nl|^hr|^cs|^da|^et|^fi|^el|^hu|^ga|^it|^lv|^lb|^mt|^nb|^nn|^pl|^pt|^sk|^sv")


                    } """)
sparql.setReturnFormat(JSON)
#wdquerycount = wdquerycount + 1

time.sleep(1.5)
wddict = sparql.query().convert()
datalist = wddict['results']['bindings']

langdict = {}
for item in datalist:
    languri = 'http://lexvo.org/id/iso639-3/'+item['isocode']['value']
    if languri not in langdict:
        langdict[languri] = {'labels':{}}
    langdict[languri]['wdqid'] = item['lang']['value']
    langdict[languri]['labels'][item['langNamelang']['value']] = item['langName']['value']
#    if languri not in langdict:
#        langdict[languri] = {'wdqid':item['lang']['value'] ,'labels':{item['langNamelang']['value']:item['langName']['value']}]}
#    else:
#        if item['langNamelang']['value'] not in langdict[languri]['labels']:
#            langdict[languri]['labels'].append({"labelLang":item['langNamelang']['value'],"label":item['langName']['value']})

print(langdict)
with open('D:/LexBib/languages/langdict.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(langdict, json_file, indent=2)
