import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv
import langmapping

with open(config.datafolder+'languages/wikidata_iso3.csv', 'r', encoding="utf-8") as csvfile:
	wdlangs = csv.DictReader(csvfile)
	langs = []
	for wdlang in wdlangs:
		langs.append(wdlang)

	count = 0
	for lang in langs:


		iso = lang['iso3']
		print('\nNow processing ['+iso+'], '+str(len(langs)-count)+' items left.')

		lanqid = langmapping.getqidfromiso(iso)
		if lanqid == None:
			lanqid = lwb.newitemwithlabel("Q8", "en", lang['langLabel'])
			lwb.setdescription(lanqid, "en", "a natural language")
			statement = lwb.stringclaim(lanqid, "P2", lang['lang'].replace("http://www.wikidata.org/entity/",""))
			statement = lwb.stringclaim(lanqid, "P32", iso)
			if 'glcodes' in lang:
				glcodes = lang['glcodes'].split(";")
				for glcode in glcodes:
					if len(glcode) > 1:
						statement = lwb.stringclaim(lanqid, "P132", glcode)
		else:
			print('Language '+lang['langLabel']+' is already there: '+lanqid)

		count += 1
