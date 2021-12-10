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

# ask for file to process
print('Please select Lexonomy XML download to be processed.')
Tk().withdraw()
download_file = askopenfilename()
print('This file will be processed: '+download_file)
try:
	tree = ElementTree.parse(download_file)
except Exception as ex:
	print ('Error: file does not exist, or XML cannot be loaded.')
	print (str(ex))
	sys.exit()

# load owl:sameAs redirect mappings

query = """
PREFIX lwb: <http://lexbib.elex.is/entity/>
PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
PREFIX lp: <http://lexbib.elex.is/prop/>
PREFIX lps: <http://lexbib.elex.is/prop/statement/>
PREFIX lpq: <http://lexbib.elex.is/prop/qualifier/>
PREFIX lpr: <http://lexbib.elex.is/prop/reference/>
PREFIX lno: <http://lexbib.elex.is/prop/novalue/>

select ?redirected ?term ?label where
{?redirected owl:sameAs ?term.
#?term ldp:P5 lwb:Q7;
#       rdfs:label ?label.
# filter(lang(?label)="en")
}"""
print("Loading owl:sameAs mappings. Waiting for LexBib v3 SPARQL...")
sparqlresults = sparql.query('https://lexbib.elex.is/query/sparql',query)
print('Got data from LexBib v3 SPARQL.')
#go through sparqlresults
redirects = {}
for row in sparqlresults:
	item = sparql.unpack_row(row, convert=None, convert_type={})
	redirects[item[0].replace('http://lexbib.elex.is/entity/','')] = item[1].replace('http://lexbib.elex.is/entity/','')
print(str(redirects))
completedterms = {}
completedlangs = {}
equivs = {}
termqidlist = []

root = tree.getroot()
count = 0
for entry in root:
	count += 1
	# if count < 123:
	# 	continue
	termqid = entry.attrib['lexbib_id']
	print('\n['+str(count)+'] Now processing term '+termqid+'...')
	while termqid in redirects:
		termqid = redirects[termqid]
		print('This term Qid redirects to '+termqid)
	termqidlist.append(termqid)
	for translations in entry.findall("translations"):
		for translation in translations:
			lang = re.search('^term_(\w+)',translation.tag).group(1)
			wikilang = langmapping.getWikiLangCode(lang)
			if wikilang == "eu":
				continue
			status = translation.attrib["status"]
			if status == "COMPLETE":
				status == "COMPLETED" # a bug in the lexvoc lexonomy style defs (both exist)
			prefLabel = translation.findall("label")[0].text
			altLabels = translation.findall("altlabel")
			if prefLabel and status != "MISSING":
			#if prefLabel and (status == "COMPLETED" or status == "COMPLETE"):
				prefLabelStatement = lwb.updateclaim(termqid,"P129",{'language':wikilang,'text':prefLabel.strip()},"monolingualtext")
				lwb.setqualifier(termqid,"P129",prefLabelStatement,"P128",status,"string")
				if altLabels:
					for altLabel in altLabels:
						if altLabel.text:
							altLabelStatement = lwb.updateclaim(termqid,"P130",{'language':wikilang,'text':altLabel.text.strip()},"monolingualtext")
							lwb.setqualifier(termqid,"P130",altLabelStatement,"P128",status,"string")
				if prefLabel and status == "COMPLETED":
					lwb.setlabel(termqid,wikilang,prefLabel.strip(),type="label")
					aliasstring = ""
					if altLabels:
						for altLabel in altLabels:
							if altLabel.text:
								aliasstring += "|"+altLabel.text.strip()
						lwb.setlabel(termqid,wikilang,aliasstring[1:],type="alias",set=True)

					if termqid not in completedterms:
						completedterms[termqid] = []
					if lang not in completedterms[termqid]:
						completedterms[termqid].append(lang)
					if lang not in completedlangs:
						completedlangs[lang] = []
					if termqid not in completedlangs[lang]:
						completedlangs[lang].append(termqid)
					if termqid not in equivs:
						equivs[termqid] = {}
					if lang not in equivs[termqid]:
						equivs[termqid][lang] = {}
					equivs[termqid][lang]['prefLabel'] = prefLabel.strip()
					if len(altLabels) > 0:
						equivs[termqid][lang]['altlabels'] = []
						for altlabel in altLabels:
							if altLabel.text:
								equivs[termqid][lang]['altlabels'].append(altlabel.text.strip())


result = {'completed_terms':completedterms,'completed_langs':completedlangs}
date = time.strftime("%Y%m%d")
with open('D:/LexBib/lexonomy/stats/completed_'+date+'.json', "w", encoding="utf-8") as jsonfile:
	json.dump(result, jsonfile, indent=2)
with open('D:/LexBib/lexonomy/completed_translations_'+date+'.json', "w", encoding="utf-8") as jsonfile:
	json.dump(equivs, jsonfile, indent=2)
with open('D:/LexBib/lexonomy/stats/terms_in_Lexonomy.json', "w", encoding="utf-8") as jsonfile:
	json.dump(termqidlist, jsonfile, indent=2)


print ('\nFinished.')
