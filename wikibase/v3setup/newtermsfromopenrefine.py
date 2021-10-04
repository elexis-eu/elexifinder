import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv
import langmapping
import requests
import time

print ('This is to copy multilingual labels from wikidata, for the following languages:')

allowed_languages = []
for iso3lang in langmapping.langcodemapping: # gets LexVoc elexis languages
	allowed_languages.append(langmapping.getWikiLangCode(iso3lang))
print(str(allowed_languages))


with open(config.datafolder+'terms/newterms-from-openrefine.csv', 'r', encoding="utf-8") as csvfile:
	lines = csv.DictReader(csvfile)

	for line in lines:
		lwbqid = line['Term'].replace("http://lexbib.elex.is/entity/","")
		print('\nNow processing: '+lwbqid,line['enPrefLabel'])
		if line['wd_qid'].startswith("Q"):
			wdqid = line['wd_qid']
			statement = lwb.updateclaim(lwbqid, "P2", wdqid, "string")
			# get wd preflabel and write to lwb
			print('Will now get labels for LWB item: '+lwbqid+' from wdItem: '+wdqid)
			done = False
			while (not done):
				try:
					r = requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=labels&ids="+wdqid).json()
					#print(str(r))
					if "labels" in r['entities'][wdqid]:
						for labellang in r['entities'][wdqid]['labels']:
							if labellang in allowed_languages:
								value = r['entities'][wdqid]['labels'][labellang]['value']
								existinglabel = lwb.getlabel(lwbqid,labellang)
								if not existinglabel:
									lwb.setlabel(lwbqid,labellang,value)
								else:
									if existinglabel.lower() != value.lower():
										lwb.setlabel(lwbqid,labellang,value, type="alias")
						done = True
				except Exception as ex:
					print('Wikidata: Label copy operation failed, will try again...\n'+str(ex))
					time.sleep(4)
			# get wd def and write to lwb
			done = False
			while (not done):
				try:
					r = requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=descriptions&ids="+wdqid).json()
					#print(str(r))
					if "descriptions" in r['entities'][wdqid]:
						for labellang in r['entities'][wdqid]['descriptions']:
							if labellang == "en":
								value = r['entities'][wdqid]['descriptions'][labellang]['value']
								statement = lwb.updateclaim(lwbqid,"P80",value,"string")
								lwb.setref(statement,"P2",wdqid,"string")
						done = True
				except Exception as ex:
					print('Wikidata: Definition copy operation failed, will try again...\n'+str(ex))
					time.sleep(4)
