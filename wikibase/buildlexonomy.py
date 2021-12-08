import xml.etree.ElementTree as xml
from xml.dom import minidom
import json
import langmapping
import os
import sys
import config
import time
import sparql
import requests

# get SKOS relations for all Q7 concepts from SPARQL query result (SKOS4Lexonomy query saved as JSON-LD) > LexBib subjects SKOS vocab
with open('D:/LexBib/terms/LexVoc4Lexonomy_test.json', encoding="utf-8") as f:
	skos =  json.load(f, encoding="utf-8")
	terms = {}
	for item in skos['results']['bindings']:
		terms[item['term_id']['value']] = {
		"enPrefLabel" : item['enPrefLabel']['value'],
		#"altLabels" : item['subjectAltLabels']['value'].split("@"),
		"broaders" : item['broaderLabels']['value'].split("@"),
		"narrowers" : item['narrowerLabels']['value'].split("@"),
		"closeMatches" : item['closeMatchLabels']['value'].split("@"),
		"related" : item['relatedLabels']['value'].split("@"),
		"definitions" : item['definitions']['value'],
		"counts" : item['corpus']['value']
		}
		if 'wd' in item:
			terms[item['term_id']['value']]['wikidata'] = item['wd']['value']
		if 'babelnet_synset' in item:
			terms[item['term_id']['value']]['babelnet'] = item['babelnet_synset']['value']
print ('\nSKOS relations loaded from saved query result.\n')
#print(str(terms))

# print('Will now get valid SKOS concepts: concepts that have a skos:broader+ relation to one of the LexVoc facet nodes, and their closeMatch concepts, in case they have attestations in LexBib English corpus.')
# sys.path.insert(0, './sparql')
# import skos4lexonomy
# print(skos4lexonomy.query)
#
# url = "https://data.lexbib.org/query/sparql"
# print("Waiting for SPARQL...")
# sparqlresults = sparql.query(url,skos4lexonomy.query)
# print('\nGot list of valid vocab items and labels from LexBib SPARQL.')
#
# terms = {}
# for row in sparqlresults:
# 	item = sparql.unpack_row(row, convert=None, convert_type={})
# 	term[item[0]] = {'counts':item[1]}

for term in terms:
	print('\nNow processing term: '+term)
	try:
		termdata = requests.get("https://lexbib.elex.is/w/api.php?action=wbgetentities&format=json&ids="+term).json()['entities'][term]
	except:
		print('*** FAILED getting lexbib entity data for '+term)
	print('Got lexbib entity data for '+term)
	if 'wikidata' in terms[term]:
		try:
			wdtermdata = requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids="+terms[term]['wikidata']).json()['entities'][terms[term]['wikidata']]
			print('Got wikidata entity data for '+terms[term]['wikidata'])
			#print(str(wdtermdata))
			#time.sleep(1)
		except:
			print('*** FAILED getting wikidata entity data for '+terms[term]['wikidata'])
	else:
		wdtermdata = {'labels' : {}, 'aliases' : {}, 'claims' : {}}

	p129langs = []
	if "P129" in termdata['claims']:
		for claim in termdata['claims']['P129']:
			p129langs.append(claim['mainsnak']['datavalue']['value']['language'])
	p130langs = []
	if "P130" in termdata['claims']:
		for claim in termdata['claims']['P130']:
			p130langs.append(claim['mainsnak']['datavalue']['value']['language'])
	print('Found '+str(len(p129langs))+' P129 and '+str(len(p130langs))+' P130langs.')


	#print(termdata)
	terms[term]['prefLabels'] = {}
	terms[term]['altLabels'] = {}
	for isolang in langmapping.langcodemapping:
		#print('Now processing language: '+isolang)
		wikilang = langmapping.getWikiLangCode(isolang)

		prefLabelDone = False
		# get preflabels
		if wikilang in termdata['labels']: # get prefLabel from LexBib wikibase (preferred, all manual "COMPLETED" translations and LexBib direct label edits are there)
			terms[term]['prefLabels'][isolang] = {'label': termdata['labels'][wikilang]['value'], 'status': 'COMPLETED'}
			print('Got prefLabel from a COMPLETED entry.')
			prefLabelDone = True

		if not prefLabelDone and wikilang in p129langs: # check for "TO CHECK" entry (second option)
			for claim in termdata['claims']['P129']:
				if claim['mainsnak']['datavalue']['value']['language'] == wikilang:
					if 'qualifiers' in claim:
						if 'P128' in claim['qualifiers']:
							for quali in claim['qualifiers']['P128']:
								if quali['datavalue']['value'] == "TO CHECK":
									terms[term]['prefLabels'][isolang] = {'label': claim['mainsnak']['datavalue']['value']['text'], 'status': 'TO CHECK'}
									print('Got prefLabel from a TO CHECK entry.')
									#time.sleep(1)
									prefLabelDone = True

		if not prefLabelDone and wikilang in wdtermdata['labels']: # get prefLabel from Wikidata (third option)
			terms[term]['prefLabels'][isolang] = {'label': wdtermdata['labels'][wikilang]['value'], 'status': 'AUTOMATIC'}
			print('Got prefLabel from wikidata: '+wdtermdata['labels'][wikilang]['value'])
			prefLabelDone = True

		if not prefLabelDone and wikilang in p129langs: # fourth option: check for prefLabel from BabelNet drafting (Lexonomy "AUTOMATIC")
			for claim in termdata['claims']['P129']:
				if claim['mainsnak']['datavalue']['value']['language'] == wikilang:
					if 'qualifiers' in claim:
						if 'P128' in claim['qualifiers']:
							for quali in claim['qualifiers']['P128']:
								if quali['datavalue']['value'] == "AUTOMATIC":
									terms[term]['prefLabels'][isolang] = {'label': claim['mainsnak']['datavalue']['value']['text'], 'status': 'AUTOMATIC'}
									print('Got prefLabel from an AUTOMATIC entry.')
									#time.sleep(1)
									prefLabelDone = True

		if not prefLabelDone:
			terms[term]['prefLabels'][isolang] = {'label': None, 'status': 'MISSING'}
			print('No preflabel found for '+isolang)

		altLabelDone = False
		# get altLabels
		terms[term]['altLabels'][isolang] = []

		if wikilang in termdata['aliases']:
			for alias in termdata['aliases'][wikilang]:
				if alias['value'].lower() != terms[term]['prefLabels'][isolang]['label'].lower():
					terms[term]['altLabels'][isolang].append(alias['value'])
					print('Got altLabel from a COMPLETED entry.')
					altLabelDone = True

		if (not altLabelDone) and (terms[term]['prefLabels'][isolang]['status'] != 'COMPLETED'):
			if terms[term]['prefLabels'][isolang]['status'] == 'TO CHECK':
				if wikilang in p130langs:
					for claim in termdata['claims']['P130']:
						if claim['mainsnak']['datavalue']['value']['language'] == wikilang:
							if 'qualifiers' in claim:
								if 'P128' in claim['qualifiers']:
									for quali in claim['qualifiers']['P128']:
										if quali['datavalue']['value'] == "TO CHECK":
											terms[term]['altLabels'][isolang].append(claim['mainsnak']['datavalue']['value']['text'])
											print('Got altLabel from a TO CHECK entry.')
											altLabelDone = True
			elif terms[term]['prefLabels'][isolang]['status'] == 'AUTOMATIC':
				existinglabels = {terms[term]['prefLabels'][isolang]['label'].lower()}
				newaltlabels = []
				if wikilang in wdtermdata['labels']:
					if wdtermdata['labels'][wikilang]['value'].lower() not in existinglabels:
						existinglabels.add(wdtermdata['labels'][wikilang]['value'].lower())
						newaltlabels.append(wdtermdata['labels'][wikilang]['value'])
					if wikilang in wdtermdata['aliases']:
						for alias in wdtermdata['aliases'][wikilang]:
							if alias['value'].lower() not in existinglabels:
								existinglabels.add(alias['value'].lower())
								newaltlabels.append(alias['value'])
								print('Got an altlabel from wikidata: '+alias['value'])


				if wikilang in p130langs:
					for claim in termdata['claims']['P130']:
						if claim['mainsnak']['datavalue']['value']['language'] == wikilang: # accept just any altlabel in that language
							if claim['mainsnak']['datavalue']['value']['text'].lower() not in existinglabels:
								existinglabels.add(claim['mainsnak']['datavalue']['value']['text'].lower())
								newaltlabels.append(claim['mainsnak']['datavalue']['value']['text'])

				for newaltlabel in newaltlabels:
					terms[term]['altLabels'][isolang].append(newaltlabel)
			else:
				pass
				print('No altlabel found for '+isolang)

with open('D:/LexBib/terms/LexVoc4Lexonomy_transformed.json', 'w' , encoding="utf-8") as f:
	json.dump(terms, f, indent=2)
	print('Finished transformation. Results in D:/LexBib/terms/LexVoc4Lexonomy_transformed.json.\n')

# build xml

for isolang in langmapping.langcodemapping.keys():
	if isolang == "eng": # no Lexonomy dict for English
		continue
	print('\nNow processing dict for language: '+isolang)
	root = xml.Element('dictionary_'+isolang)

	for lwbqid in terms:
		#time.sleep(0.5)
		print('\nNow processing term: '+lwbqid)
		entry = xml.Element('entry')
		root.append(entry)
		entry.set('lexbib_id',lwbqid)
		#status_entry = xml.SubElement(entry, 'status_entry')
		term = xml.SubElement(entry, 'term')
		term.set('found_in_articles',terms[lwbqid]['counts'])
		label_eng = xml.SubElement(term, 'label_eng')
		label_eng.text = terms[lwbqid]['enPrefLabel']

		#processed_prefLabels.append(babeltranslations['prefLabel'])
		if 'en' in terms[lwbqid]['altLabels']:
			for item in terms[lwbqid]['altLabels']['en']:
				if len(item) > 0:
					altlabel_eng = xml.SubElement(term, 'altlabel_eng')
					altlabel_eng.text = item
		for item in terms[lwbqid]['broaders']:
			if len(item) > 0:
				broader = xml.SubElement(term, 'broader_eng')
				broader.text = item
		for item in terms[lwbqid]['narrowers']:
			if len(item) > 0:
				narrower = xml.SubElement(term, 'narrower_eng')
				narrower.text = item

		for item in terms[lwbqid]['closeMatches']:
			if len(item) > 0:
				closeM = xml.SubElement(term, 'closematch_eng')
				closeM.text = item

		for item in terms[lwbqid]['related']:
			if len(item) > 0:
				related = xml.SubElement(term, 'related_eng')
				related.text = item

		definition = xml.SubElement(term, 'definition_eng')
		definition.text = terms[lwbqid]['definitions'].replace("@", " | ")

		Babelnet_ID = xml.SubElement(term, 'Babelnet_ID')
		if 'babelnet' not in terms[lwbqid]:
			Babelnet_ID.text = "None"
		else:
			Babelnet_ID.text = terms[lwbqid]['babelnet']
			#Babelnet_ID.set('match_quality',babeltranslations['status'])

		translation = xml.SubElement(entry, 'translation')
		translation.set('language',isolang)
		status_translation = xml.SubElement(translation, 'status_translation')

		if isolang in terms[lwbqid]['prefLabels']:
			label = xml.SubElement(translation, 'label')
			if terms[lwbqid]['prefLabels'][isolang]['label']:
				label.text = terms[lwbqid]['prefLabels'][isolang]['label']
			status_translation.text = terms[lwbqid]['prefLabels'][isolang]['status']
		else:
			print('Missing prefLabel for term '+lwbqid+', language '+isolang)
			status_translation.text = "MISSING"

		if isolang in terms[lwbqid]['altLabels']:

			for altlabel in terms[lwbqid]['altLabels'][isolang]:
				altlabelelement = xml.SubElement(translation, 'altlabel')
				altlabelelement.text = altlabel
		else:
			print('Missing altLabels for term '+lwbqid+', language '+isolang)

	reparsed = minidom.parseString(xml.tostring(root, 'utf-8')).toprettyxml(indent = "\t")
	print(str(reparsed))
	outfile = 'D:/LexBib/lexonomy/upload/lexonomy_upload_'+isolang+'.xml'
	with open(outfile, "w", encoding="utf-8") as file:
		file.write(reparsed)
	print('Wrote to '+outfile)

print('Finished. Results in D:/LexBib/lexonomy/upload/.')
