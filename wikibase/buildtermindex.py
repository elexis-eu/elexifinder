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

import requests
import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))

#
import nlp
import langmapping
import config
from stoptermlabels import stoptermlabels

keydict = {}
keyindex = {}
# one keywordprocessor for every language to process:
keyword_processor = {"eng": KeywordProcessor(), "spa": KeywordProcessor()}

def feed_keywords(isolang):
	global keyindex
	global keydict
	global keyword_processor
	wikilang = '"'+langmapping.getWikiLangCode(isolang)+'"'
	# get valid SKOS concepts and labels:
	# concepts that have a skos:broader+ relation to a facet of Q1 "Lexicography", and their closeMatch concepts.
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
	print("Waiting for SPARQL... Getting LexVoc concepts for lang: "+isolang)
	sparqlresults = sparql.query(url,query)
	print('\nGot list of valid vocab items and labels from LexBib SPARQL.')
	print('Now feeding KeywordProcessor for '+isolang+'...')
	#go through sparqlresults
	# build dict for keyword processor
	rowindex = 0
	keydict[isolang] = {}
	keyindex[isolang] = {}
	for row in sparqlresults:
		rowindex += 1
		item = sparql.unpack_row(row, convert=None, convert_type={})
		#print('\nNow processing item ['+str(rowindex)+']:\n'+str(item))
		termqids = item[1].split(";")
		termlabel = item[0].lower() # convert term label to lower case
		#if entry['concept']['value'] in erdict: # add only to keyword processor if present in elexifinder categories dict.

		if termlabel in stoptermlabels[isolang]:
			continue

		if "-" not in termlabel:
			termlabellem = nlp.lemmatize_clean(termlabel, lang=isolang)[0]
		else:
			termlabellem = None
		if termlabellem != None and termlabellem != termlabel:
			termlabellist = [termlabel, termlabellem]
		else:
			termlabellist = [termlabel]
		keydict[isolang][str(rowindex)] = termlabellist
		for termqid in termqids:
			if str(rowindex) not in keyindex[isolang]:
				keyindex[isolang][str(rowindex)] = [termqid]
			else:
				keyindex[isolang][str(rowindex)].append(termqid)



	with open(config.datafolder+'bodytxt/keyword_processor_keydict_'+isolang+'_last.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
		json.dump(keydict[isolang], json_file, indent=2)
	with open(config.datafolder+'bodytxt/keyindex_'+isolang+'_last.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
		json.dump(keyindex[isolang], json_file, indent=2)


	keyword_processor[isolang].add_keywords_from_dict(keydict[isolang])

	print('\n***Keyword processor fed for language '+isolang+'\n')

# load bodytxt collection
with open(config.datafolder+'bodytxt/bodytxt_collection.json', encoding="utf-8") as infile:
	bodytxtcoll = json.load(infile)

# load keyword processor
termstats = {}
for isolang in keyword_processor:
	feed_keywords(isolang)
	termstats[isolang] = {}

#go through items with bodytxt
rowindex = 0
foundterms = {}

for bibItem in bodytxtcoll:
	rowindex += 1
	print('\nNow processing item ['+str(rowindex)+'] of '+str(len(bodytxtcoll))+':')

	isolang = bodytxtcoll[bibItem]['lang']

	# load txt.
	bodytxt = bodytxtcoll[bibItem]['bodytxt']
	cleantext = bodytxtcoll[bibItem]['bodylemclean']
	bodytxtsource = bodytxtcoll[bibItem]['source']

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
	keywords = keyword_processor[isolang].extract_keywords(cleantext[0])
	keywords = sorted(keywords,key=keywords.count,reverse=True) # sorts according to frequency in the text
	foundterms[bibItem] = {}
	uniqkws = list(OrderedDict.fromkeys(keywords))
	for uniqkw in uniqkws:
		hits = keywords.count(uniqkw)
		termqids = keyindex[isolang][uniqkw]
		for termqid in termqids:
			if termqid not in termstats:
				termstats[isolang][termqid] = 1
			else:
				termstats[isolang][termqid] += 1
			if termqid not in foundterms[bibItem]:
				foundterms[bibItem][termqid] = {'hits': hits, 'rfreq': hits/cleantext[1]}
			else:
				foundterms[bibItem][termqid]['hits'] += hits
				foundterms[bibItem][termqid]['rfreq'] += hits/cleantext[1]

	print('This lemcleantext ['+str(cleantext[1])+' tokens] contains '+str(len(foundterms[bibItem]))+' term candidates. Language was '+isolang+'.')



with open(config.datafolder+'bodytxt/foundterms_'+time.strftime("%Y%m%d-%H%M%S")+'.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(foundterms, json_file, indent=2)
with open(config.datafolder+'bodytxt/termstats_'+time.strftime("%Y%m%d-%H%M%S")+'.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(termstats, json_file, indent=2)
with open(config.datafolder+'bodytxt/termstats_last.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(termstats, json_file, indent=2)
