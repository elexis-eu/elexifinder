import time
import sys
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

with open(config.datafolder+'terms/lexbiblegacywikiterms.txt', 'r') as infile:
	items_to_update = infile.read().split('\n')
print('\n'+str(len(items_to_update))+' items will be updated.')

itemcount = 0
for lwbqid in items_to_update:
	wdqid = lwb.wdids[lwbqid]
	print('\nItem ['+str(itemcount)+'], '+str(len(items_to_update)-itemcount)+' items left.')
	print('Will now get labels for LWB item: '+lwbqid+' from wdItem: '+wdqid)
	done = False
	while (not done):
		try:
			r = requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=aliases&ids="+wdqid).json()
			#print(str(r))
			if "aliases" in r['entities'][wdqid]:
				for labellang in r['entities'][wdqid]['aliases']:
					if labellang in allowed_languages:
						existaliases = lwb.getaliases(lwbqid,labellang)
						existinglabels = [lwb.getlabel(lwbqid,labellang)]
						for existalias in existaliases:
							existinglabels.append(existalias.lower())
						for label in r['entities'][wdqid]['aliases'][labellang]:
							if label['value'].lower() not in existinglabels:
								lwb.setlabel(lwbqid,labellang,label['value'],type="alias")
				done = True

		except Exception as ex:
			print('Wikidata: Label copy operation failed, will try again...\n'+str(ex))
			time.sleep(4)

	itemcount += 1
