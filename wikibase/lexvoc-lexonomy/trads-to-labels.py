import lxml
from xml.etree import ElementTree
import re
import os
import sys
sys.path.insert(1, os.path.realpath(os.path.pardir))
import lwb
import config
import langmapping
import time
import json
import sparql
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def langstringdict(sparqlresult):
	if not sparqlresult:
		return {}
	ldict = {}
	for langstring in sparqlresult.split("|"):
		s = langstring.split("@")[0]
		l = langstring.split("@")[1]
		if l not in ldict:
			ldict[l] = [s]
		else:
			ldict[l].append(s)
	return ldict

# load translations

query = """
PREFIX lwb: <https://lexbib.elex.is/entity/>
PREFIX ldp: <https://lexbib.elex.is/prop/direct/>
PREFIX lp: <https://lexbib.elex.is/prop/>
PREFIX lps: <https://lexbib.elex.is/prop/statement/>
PREFIX lpq: <https://lexbib.elex.is/prop/qualifier/>
PREFIX lpr: <https://lexbib.elex.is/prop/reference/>
PREFIX lno: <https://lexbib.elex.is/prop/novalue/>

select ?Term
(group_concat(distinct concat(?PrefTrad,"@",lang(?PrefTrad));SEPARATOR="|") as ?PrefTrads)
(group_concat(distinct concat(?AltTrad,"@",lang(?AltTrad));SEPARATOR="|") as ?AltTrads)

where {
  ?facet ldp:P131 lwb:Q1 .
  ?Term ldp:P5 lwb:Q7 ;
        ldp:P72* ?facet ;
        lp:P129 [lps:P129 ?PrefTrad ; lpq:P128 "COMPLETED"] .
 OPTIONAL { ?Term lp:P130 [lps:P130 ?AltTrad ; lpq:P128 "COMPLETED"] . }

  } group by ?Term ?PrefTrads ?AltTrads
"""
print("Loading translations. Waiting for LexBib v3 SPARQL...")
sparqlresults = sparql.query('https://lexbib.elex.is/query/sparql',query)
print('Got data from LexBib v3 SPARQL.')
#go through sparqlresults
translations = {}
for row in sparqlresults:
	item = sparql.unpack_row(row, convert=None, convert_type={})
	preftransdict = langstringdict(item[1])
	alttransdict = langstringdict(item[2])
	translations[item[0].replace('https://lexbib.elex.is/entity/','')] = {'preftrans':preftransdict,'alttrans':alttransdict}
print(str(translations))

# load labels

query = """
PREFIX lwb: <https://lexbib.elex.is/entity/>
PREFIX ldp: <https://lexbib.elex.is/prop/direct/>
PREFIX lp: <https://lexbib.elex.is/prop/>
PREFIX lps: <https://lexbib.elex.is/prop/statement/>
PREFIX lpq: <https://lexbib.elex.is/prop/qualifier/>
PREFIX lpr: <https://lexbib.elex.is/prop/reference/>
PREFIX lno: <https://lexbib.elex.is/prop/novalue/>

select ?Term
(group_concat(distinct concat(?PrefLabel,"@",lang(?PrefLabel));SEPARATOR="|") as ?PrefLabels)
(group_concat(distinct concat(?AltLabel,"@",lang(?AltLabel));SEPARATOR="|") as ?AltLabels)


where {
  ?facet ldp:P131 lwb:Q1 .
  ?Term ldp:P5 lwb:Q7;
        ldp:P72* ?facet ;
        rdfs:label ?PrefLabel.
 OPTIONAL { ?Term skos:altLabel ?AltLabel. }

  } group by ?Term ?PrefLabels ?AltLabels
"""
print("Loading labels. Waiting for LexBib v3 SPARQL...")
sparqlresults = sparql.query('https://lexbib.elex.is/query/sparql',query)
print('Got data from LexBib v3 SPARQL.')
#go through sparqlresults

for row in sparqlresults:
	item = sparql.unpack_row(row, convert=None, convert_type={})
	termqid = item[0].replace('https://lexbib.elex.is/entity/','')
	if termqid not in translations: #only process terms that have at least one Lexonomy "COMPLETED" translation
		continue
	preflabeldict = langstringdict(item[1])
	print('\nTerm '+termqid+' found in translations dictionary. English prefLabel: '+preflabeldict['en'][0])
	altlabeldict = langstringdict(item[2])
	for lang in translations[termqid]['preftrans']:
		#print('Now processing language '+lang)
		if lang == "cnr":
			continue
		if lang not in preflabeldict:
				preflabeldict[lang] = []
		for preftrans in translations[termqid]['preftrans'][lang]:
			#print('Now processing '+preftrans+' for '+lang)
			if preftrans not in preflabeldict[lang]:
				lwb.setlabel(termqid,lang,preftrans,type="label")
			else:
				print('PrefLabel '+preftrans+' for language '+lang+' already there.')
	for lang in translations[termqid]['alttrans']:
		if lang == "cnr":
			continue

		newaliases = []
		oldgoodaliases = []
		if lang not in altlabeldict:
			altlabeldict[lang] = []
		if  len(altlabeldict[lang]) > len(translations[termqid]['alttrans'][lang]): #if there are old left-over altlabels, erase and re-do altlabels
			altlabeldict[lang] = []
		for alttrans in translations[termqid]['alttrans'][lang]:
			if alttrans not in altlabeldict[lang]:
				newaliases.append(alttrans)
				print('Found new alias '+alttrans+' for language '+lang)
			else:
				#print('AltLabel '+alttrans+' for language '+lang+' already there.')
				altlabeldict[lang].remove(alttrans)
				oldgoodaliases.append(alttrans)
		if len(altlabeldict[lang]) > 0: # overwrite set of aliases
			print('There are some old aliases left for language '+lang+', will re-write aliases: '+str(altlabeldict[lang]))
			lwb.setlabel(termqid,lang,newaliases+oldgoodaliases,type="alias",set=True)
		elif len(newaliases) > 0: # just add new aliases
			lwb.setlabel(termqid,lang,newaliases,type="alias",set=False)
		else:
			print('All alias translations already there for language '+lang)



print ('\nFinished.')
