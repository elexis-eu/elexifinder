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


completedterms = {}
completedlangs = {}
equivs = {}
termqidlist = []

root = tree.getroot()

for entry in root:
	#time.sleep(2)
	termqid = entry.attrib['lexbib_id']
	termqidlist.append(termqid)
	for translations in entry.findall("translations"):
		for translation in translations:
			lang = re.search('^term_(\w+)',translation.tag).group(1)
			wikilang = langmapping.getWikiLangCode(lang)
			status = translation.attrib["status"]
			prefLabel = translation.findall("label")[0].text
			altLabels = translation.findall("altlabel")
			if status != "MISSING":
				prefLabelStatement = lwb.updateclaim(termqid,"P129",{'language':wikilang,'text':prefLabel},"monolingualtext")
				lwb.setqualifier(termqid,"P129",prefLabelStatement,"P128",status,"string")
				for altLabel in altLabels:
					altLabelStatement = lwb.updateclaim(termqid,"P130",{'language':wikilang,'text':altLabel.text},"monolingualtext")
					lwb.setqualifier(termqid,"P129",altLabelStatement,"P128",status,"string")



			if status == "COMPLETED":
				lwb.setlabel(termqid,wikilang,prefLabel,type="label")
				aliasstring = ""
				for altLabel in altLabels:
					aliasstring += "|"+altLabel.text
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
				equivs[termqid][lang]['prefLabel'] = prefLabel
				if len(altLabels) > 0:
					equivs[termqid][lang]['altlabels'] = []
					for altlabel in altLabels:
						equivs[termqid][lang]['altlabels'].append(altlabel.text)


result = {'completed_terms':completedterms,'completed_langs':completedlangs}
date = time.strftime("%Y%m%d")
with open('D:/LexBib/lexonomy/stats/completed_'+date+'.json', "w", encoding="utf-8") as jsonfile:
	json.dump(result, jsonfile, indent=2)
with open('D:/LexBib/lexonomy/completed_translations_'+date+'.json', "w", encoding="utf-8") as jsonfile:
	json.dump(equivs, jsonfile, indent=2)
with open('D:/LexBib/lexonomy/stats/terms_in_Lexonomy.json', "w", encoding="utf-8") as jsonfile:
	json.dump(termqidlist, jsonfile, indent=2)


print ('\nFinished.')
