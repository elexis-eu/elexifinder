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

# get valid SKOS concepts and labels:
# concepts that have a skos:broader+ relation to Q1 "Lexicography, and their closeMatch concepts.
query = """
PREFIX lwb: <http://lexbib.elex.is/entity/>
PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
PREFIX lp: <http://lexbib.elex.is/prop/>
PREFIX lps: <http://lexbib.elex.is/prop/statement/>
PREFIX lpq: <http://lexbib.elex.is/prop/qualifier/>

select distinct (strafter(str(?concepturi),"http://lexbib.elex.is/entity/") as ?concept) ?termLabel where {
  ?concepturi ldp:P5 lwb:Q7 .
 { ?concepturi ldp:P72* lwb:Q1 .} # present in narrower-broader-tree with "Lexicography" as root node
  UNION
 {?concepturi ldp:P77 ?closeMatch. ?closeMatch ldp:P72* lwb:Q1 . } # includes closeMatch items without own broader-rels
  ?concepturi rdfs:label|skos:altLabel ?termLabel . FILTER (lang(?termLabel)="en")
} ORDER BY ?concept

# select distinct (strafter(str(?concepturi),"http://lexbib.elex.is/entity/") as ?concept) ?termLabel where {
#
#   ?concepturi ldp:P74 lwb:Q15469 . # part of "lexinfo 3.0"
#   ?concepturi rdfs:label|skos:altLabel ?termLabel . FILTER (lang(?termLabel)="en")
# } ORDER BY ?concept

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
for row in sparqlresults:
	rowindex += 1
	item = sparql.unpack_row(row, convert=None, convert_type={})
	#print('\nNow processing item ['+str(rowindex)+']:\n'+str(item))
	termqid = item[0]
	termlabel = item[1].lower() # convert term label to lower case
	#if entry['concept']['value'] in erdict: # add only to keyword processor if present in elexifinder categories dict.
	if "-" not in termlabel:
		termlabellem = nlp.lemmatize_clean(termlabel)[0]
	else:
		termlabellem = None
	if termlabellem != None and termlabellem != termlabel:
		termlabellist = [termlabel, termlabellem]
	else:
		termlabellist = [termlabel]
	for termlabel in termlabellist:
		if termlabel in stopterms:
			continue
		if termqid not in keydict:
			keydict[termqid] = [termlabel]
		else:
			if termlabel not in keydict[termqid]: # avoid duplicate labels (e.g. "NLP" [converted to "nlp"], and "nlp")
				keydict[termqid].append(termlabel)
with open(config.datafolder+'bodytxt/keyword_processor_keydict.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(keydict, json_file, indent=2)
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
  ?bibItem ldp:P85 ?coll . # Items with Elexifinder collection only
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
		if uniqkw not in termstats:
			termstats[uniqkw] = 1
		else:
			termstats[uniqkw] += 1
		foundterms[bibItem][uniqkw] = {'hits': hits, 'rfreq': hits/cleantext[1]}

	print('This lemcleantext ['+str(cleantext[1])+' tokens] contains '+str(len(foundterms[bibItem]))+' term candidates.')

with open(config.datafolder+'bodytxt/foundterms_'+time.strftime("%Y%m%d-%H%M%S")+'.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(foundterms, json_file, indent=2)
with open(config.datafolder+'bodytxt/termstats_'+time.strftime("%Y%m%d-%H%M%S")+'.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(termstats, json_file, indent=2)
with open(config.datafolder+'bodytxt/termstats_last.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(termstats, json_file, indent=2)
