import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import time
import json
import requests
import csv
import lwb # functions for data.lexbib.org (LWB: LexBib WikiBase) I/O operations
import config
import langmapping

print ('This is to copy multilingual labels from wikidata, for the following languages:')

allowed_languages = []
for iso3lang in langmapping.langcodemapping: # gets LexVoc elexis languages
	allowed_languages.append(langmapping.getWikiLangCode(iso3lang))
print(str(allowed_languages))

with open(config.datafolder+'terms/terms_wdqids.txt', 'r') as infile:
	items_to_update = infile.read().split('\n')
print('\n'+str(len(items_to_update))+' items will be updated.')

with open(config.datafolder+'terms/terms_wdqids_done.txt', 'r') as donefile:
	done_items = donefile.read().split('\n')

itemcount = 0
for lwbqid in items_to_update:
	if lwbqid in done_items:
		print('\nItem ['+str(itemcount)+'] has been done in a previous run.')
		continue
	wdqid = lwb.wdids[lwbqid]
	print('\nItem ['+str(itemcount)+'], '+str(len(items_to_update)-itemcount)+' items left.')
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

	itemcount += 1
	with open(config.datafolder+'terms/terms_wdqids_done.txt', 'a') as outfile:
		outfile.write(lwbqid+'\n')
