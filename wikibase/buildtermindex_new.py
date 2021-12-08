## assigns term candidates to bibitems. (Term labels are found in English full texts)
import time
import re
import json
import os
import csv
from collections import OrderedDict
from datetime import datetime
import sparql
from flashtext import KeywordProcessor
keyword_processor = KeywordProcessor()
import requests
import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))

#
import nlp
import config
from stopterms import stopterms

# load bodytxt collection
with open(config.datafolder+'bodytxt/bodytxt_collection.json', encoding="utf-8") as infile:
	bodytxtcoll = json.load(infile)
missing_bodytxts = []

# get valid SKOS concepts and labels:
# concepts that have a skos:broader+ relation to Q1 "Lexicography, and their closeMatch concepts.
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

  ?s rdfs:label|skos:altLabel ?sLabel . FILTER (lang(?sLabel)="en")

}  group by ?sLabel ?uri ?count
order by desc(?count)

"""
print(query)

url = "https://lexbib.elex.is/query/sparql"
print("Waiting for SPARQL...")
sparqlresults = sparql.query(url,query)
print('\nGot list of valid vocab items and labels from LexBib SPARQL.')
print('Now feeding KeywordProcessor...')
#go through sparqlresults
# build dict for keyword processor
rowindex = 0
keydict = {}
keyindex = {}
for row in sparqlresults:
	rowindex += 1
	item = sparql.unpack_row(row, convert=None, convert_type={})
	#print('\nNow processing item ['+str(rowindex)+']:\n'+str(item))
	termqids = item[1].split(";")
	termlabel = item[0].lower() # convert term label to lower case
	#if entry['concept']['value'] in erdict: # add only to keyword processor if present in elexifinder categories dict.

	if termlabel in stopterms:
		continue

	if "-" not in termlabel:
		termlabellem = nlp.lemmatize_clean(termlabel)[0]
	else:
		termlabellem = None
	if termlabellem != None and termlabellem != termlabel:
		termlabellist = [termlabel, termlabellem]
	else:
		termlabellist = [termlabel]
	keydict[str(rowindex)] = termlabellist
	for termqid in termqids:
		if str(rowindex) not in keyindex:
			keyindex[str(rowindex)] = [termqid]
		else:
			keyindex[str(rowindex)].append(termqid)



with open(config.datafolder+'bodytxt/keyword_processor_keydict_last.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(keydict, json_file, indent=2)
with open(config.datafolder+'bodytxt/keyindex_last.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(keyindex, json_file, indent=2)


keyword_processor.add_keywords_from_dict(keydict)

print('\n***Keyword processor fed.\n')

#get bibitems to process
query = """
PREFIX lwb: <http://lexbib.elex.is/entity/>
PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
PREFIX lp: <http://lexbib.elex.is/prop/>
PREFIX lps: <http://lexbib.elex.is/prop/statement/>
PREFIX lpq: <http://lexbib.elex.is/prop/qualifier/>

select ?bibItem ?lang ?nid where
{
  #BIND(lwb:Q3901 as ?bibItem)

  ?bibItem ldp:P5 lwb:Q3 .
  ?bibItem ldp:P11 ?lang .
  filter(?lang = lwb:Q201) # English only
  #?bibItem ldp:P85 ?coll . # Items with Elexifinder collection only
  #filter not exists {?bibItem lp:P96 ?termcandstatement. } # Items with no P96 statement (value or novalue) only
  BIND(xsd:integer(strafter(str(?bibItem),"http://lexbib.elex.is/entity/Q")) as ?nid)
 } order by ?nid
"""
print(query)

url = "https://lexbib.elex.is/query/sparql"
print("Waiting for SPARQL...")
sparqlresults = sparql.query(url,query)
print('\nGot bibItem list from LexBib SPARQL.')

#go through sparqlresults
rowindex = 0
foundterms = {}
termstats = {}
for row in sparqlresults:
	rowindex += 1
	item = sparql.unpack_row(row, convert=None, convert_type={})
	print('\nNow processing item ['+str(rowindex)+']:\n'+str(item))
	bibItem = item[0].replace("http://lexbib.elex.is/entity/","")
	lang = item[1].replace("http://lexbib.elex.is/entity/","")
	nid = item[2]

	if nid < 1: # if script needs to be re-started...
		continue


	# load txt.
	if bibItem in bodytxtcoll:
		#bodytxt = bodytxtcoll[bibItem]['bodytxt']
		cleantext = bodytxtcoll[bibItem]['bodylemclean']
		bodytxtsource = bodytxtcoll[bibItem]['source']
	else:
		print('*** Missing entry in bodytxtcoll: '+bibItem)
		missing_bodytxts.append(bibItem)
		continue

	# # keyword extraction bodytxt (not lemmatized)
	# keywords = keyword_processor.extract_keywords(bodytxt)
	# keywords = sorted(keywords,key=keywords.count,reverse=True) # sorts according to frequency in the text
	# foundterms[bibItem]['bodytxt'] = {}
	# uniqkws = list(OrderedDict.fromkeys(keywords))
	# for uniqkw in uniqkws:
	# 	hits = keywords.count(uniqkw)
	# 	foundterms[bibItem]['bodytxt'][uniqkw] = {'hits': hits, 'rfreq': hits/cleantext[1]} # assumes token count from clean text as real
	#
	# print('This bodytext ['+str(cleantext[1])+' tokens] contains '+str(len(foundterms[bibItem]['bodytxt']))+' term candidates.')

	# keyword extraction cleantext
	keywords = keyword_processor.extract_keywords(cleantext[0])
	keywords = sorted(keywords,key=keywords.count,reverse=True) # sorts according to frequency in the text
	foundterms[bibItem] = {}
	uniqkws = list(OrderedDict.fromkeys(keywords))
	for uniqkw in uniqkws:
		hits = keywords.count(uniqkw)
		termqids = keyindex[uniqkw]
		for termqid in termqids:
			if termqid not in termstats:
				termstats[termqid] = 1
			else:
				termstats[termqid] += 1
			if termqid not in foundterms[bibItem]:
				foundterms[bibItem][termqid] = {'hits': hits, 'rfreq': hits/cleantext[1]}
			else:
				foundterms[bibItem][termqid]['hits'] += hits
				foundterms[bibItem][termqid]['rfreq'] += hits/cleantext[1]

	print('This lemcleantext ['+str(cleantext[1])+' tokens] contains '+str(len(foundterms[bibItem]))+' term candidates.')



with open(config.datafolder+'bodytxt/foundterms_'+time.strftime("%Y%m%d-%H%M%S")+'.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(foundterms, json_file, indent=2)
with open(config.datafolder+'bodytxt/termstats_'+time.strftime("%Y%m%d-%H%M%S")+'.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(termstats, json_file, indent=2)
with open(config.datafolder+'bodytxt/termstats_last.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(termstats, json_file, indent=2)
with open(config.datafolder+'bodytxt/missing_bodytxts_last.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(missing_bodytxts, json_file, indent=2)
