import xml.etree.ElementTree as xml
from xml.dom import minidom
import json
import langmapping
import os
import sys
import config
import time
import sparql

# get SKOS relations for all Q7 concepts from SPARQL query result (SKOS4Lexonomy query saved as JSON-LD) > LexBib subjects SKOS vocab
with open('D:/LexBib/terms/LexVoc4Lexonomy.json', encoding="utf-8") as f:
	skos =  json.load(f, encoding="utf-8")['results']['bindings']
	reldict = {}
	for item in skos:
		reldict[item['term_id']['value']] = {
		"enPrefLabel" : item['enPrefLabel']['value'],
		"enAltLabels" : item['enAltLabels']['value'].split("@"),
		"multiLabels" : json.loads("["+item['subjectLabels']['value']+"]"),
		"broaders" : item['broaderLabels']['value'].split("@"),
		"narrowers" : item['narrowerLabels']['value'].split("@"),
		"closeMatches" : item['closeMatchLabels']['value'].split("@"),
		"related" : item['relatedLabels']['value'].split("@"),
		"definitions" : item['definitions']['value'].split("@"),
		}
print ('\nSKOS relations loaded from saved query result.\n')
#print(str(reldict))

# print('Will now get valid SKOS concepts: concepts that have a skos:broader+ relation to Q1 "Lexicography", and their closeMatch concepts.')
# sys.path.insert(0, './sparql')
# import skos4lexonomy
# print(skos4lexonomy.query)
#
# url = "https://data.lexbib.org/query/sparql"
# print("Waiting for SPARQL...")
# sparqlresults = sparql.query(url,skos4lexonomy.query)
# print('\nGot list of valid vocab items and labels from LexBib SPARQL.')
#
# ercatlist = {}
# for row in sparqlresults:
# 	item = sparql.unpack_row(row, convert=None, convert_type={})
# 	if item[0] not in ercatlist:
# 		ercatlist[item[0]] = item[2]

# build xml

with open('D:/LexBib/bodytxt/termstats.json', encoding="utf-8") as f:
	termstats =  json.load(f, encoding="utf-8")

transdir = config.datafolder+'babelnet'

lexonomy_stats = {'labels_sources':{},'labels_count':{}}
babeltranslations = {}
for lwbqid in reldict:
	#time.sleep(0.5)
	filepath = os.path.join(transdir,lwbqid+'.json')
	if os.path.isfile(filepath):
		print(lwbqid+' has babelnet translations.')
		with open(filepath, 'r', encoding="utf-8") as jsonfile:
			babeltranslations[lwbqid] = json.load(jsonfile)
	else:
		babeltranslations[lwbqid] = {'term_uri':lwbqid,'translations':{}}
		print(lwbqid+' has no babelnet translations.')
	if lwbqid in termstats:
		babeltranslations[lwbqid]['conceptcount'] = termstats[lwbqid]
	else:
		babeltranslations[lwbqid]['conceptcount'] = 0

	# merge existing lwb labels to babeltranslations
	langlist = []
	for lang in langmapping.langcodemapping.keys():
		if lang == "eng":
			continue
		if lang not in langlist: # this avoids processing the same language twice, so it takes only the first entry for a language in BabelNet JSON
			#print('Now doing '+lang)
			langlist.append(lang)
			if lang not in babeltranslations[lwbqid]['translations']:
				babeltranslations[lwbqid]['translations'][lang] = []
			wikilang = langmapping.getWikiLangCode(lang)
			existing_labels = []
			existing_labels_normalized = []
			for babeltrans in babeltranslations[lwbqid]['translations'][lang]:
				existing_labels.append(babeltrans['lemma'])
				existing_labels_normalized.append(babeltrans['lemma'].lower())
			for multiLabel in reldict[lwbqid]['multiLabels']:
				if multiLabel['lang'] == wikilang:
					print('Found matching language in LexBib/BabelNet labels: '+wikilang)

					if multiLabel['text'].lower() not in existing_labels_normalized:
						babeltranslations[lwbqid]['translations'][lang].append({"lemma":multiLabel['text'],"type":"LexBib_Wikidata"})
						print('Added label from LexBib: '+multiLabel['text'])

					else:
						print('LexBib label was already there: '+multiLabel['text'])


print('\nNow writing XML files...')
for diclang in langmapping.langcodemapping.keys():
	preflabels_count = 0
	altlabels_count = 0
	root = xml.Element('dictionary_'+diclang)

	for qid in termstats: # only those terms that were found in at least 1 text

		entry = xml.Element('entry')
		root.append(entry)
		entry.set('lexbib_id',qid)
		status_entry = xml.SubElement(entry, 'status_entry')
		term = xml.SubElement(entry, 'term')
		term.set('found_in_articles',str(babeltranslations[qid]['conceptcount']))
		label_eng = xml.SubElement(term, 'label_eng')
		label_eng.text = reldict[qid]['enPrefLabel']
		#processed_prefLabels.append(babeltranslations['prefLabel'])
		for item in reldict[qid]['enAltLabels']:
			if len(item) > 0:
				altlabel_eng = xml.SubElement(term, 'altlabel_eng')
				altlabel_eng.text = item
		for item in reldict[qid]['broaders']:
			if len(item) > 0:
				broader = xml.SubElement(term, 'broader_eng')
				broader.text = item
		for item in reldict[qid]['narrowers']:
			if len(item) > 0:
				narrower = xml.SubElement(term, 'narrower_eng')
				narrower.text = item

		for item in reldict[qid]['closeMatches']:
			if len(item) > 0 and item.lower() != reldict[qid]['enPrefLabel'].lower():
				closeM = xml.SubElement(term, 'closematch_eng')
				closeM.text = item

		for item in reldict[qid]['related']:
			if len(item) > 0:
				related = xml.SubElement(term, 'related_eng')
				related.text = item

		for item in reldict[qid]['definitions']:
			if len(item) > 0:
				definition = xml.SubElement(term, 'definition_eng')
				definition.text = item

		Babelnet_ID = xml.SubElement(term, 'Babelnet_ID')
		if babeltranslations[qid] and 'bn_id' in babeltranslations[qid]:
			Babelnet_ID.text = babeltranslations[qid]['bn_id']
			Babelnet_ID.set('match_quality',babeltranslations[qid]['status'])
		else:
			Babelnet_ID.text = "None"
			Babelnet_ID.set('match_quality',"0")

		translation = xml.SubElement(entry, 'translation')
		translation.set('language',diclang)
		status_translation = xml.SubElement(translation, 'status_translation')

		if babeltranslations[qid] and babeltranslations[qid]['translations'] and diclang in babeltranslations[qid]['translations']:

			translist = []
			translist_normalized = []
			# if len(babeltranslations[qid]['translations'][diclang]) < 3:
			# 	maxtrans = len(babeltranslations[qid]['translations'][diclang])
			# else:
			maxtrans = 3 # take only the first three unique translations from babelnet
			for trans in babeltranslations[qid]['translations'][diclang]:
				translem = trans['lemma']
				transtype = trans['type']

				#print('Found translation '+translem+', '+transtype)

				if (transtype == "HIGH_QUALITY" or transtype == "LexBib_Wikidata" or transtype == "AUTOMATIC_TRANSLATION") and (translem.lower() not in translist_normalized):
					translist.append(translem)
					translist_normalized.append(translem.lower())
					if transtype in lexonomy_stats['labels_sources']:
						lexonomy_stats['labels_sources'][transtype] += 1
					else:
						lexonomy_stats['labels_sources'][transtype] = 1

					#print(lang+': Added translation: '+translem)
					#time.sleep(0.5)
				if len(translist) == maxtrans:
					break

			equivs_iter = iter(translist)
			status_translation.text = ("AUTOMATIC")
			label = xml.SubElement(translation, 'label')
			if len(translist) > 0:
				label.text = next(equivs_iter).replace("_"," ") # take the first translation as preferred translation
				preflabels_count += 1
			while True:
				try:
					altEquiv = next(equivs_iter).replace("_"," ")
				except:
					break
				altlabel = xml.SubElement(translation, 'altlabel')
				altlabel.text = altEquiv
				altlabels_count += 1
		else:
			status_translation.text = ("MISSING")

	tree_obj = xml.ElementTree(root)
	with open('D:/LexBib/lexonomy/lexonomy_upload_'+diclang+'.xml', "w", encoding='utf-8') as file:
		reparsed = minidom.parseString(xml.tostring(root, 'utf-8')).toprettyxml(indent = "\t")
		#print(reparsed)
		file.write(reparsed)
	lexonomy_stats['labels_count'][diclang] = {"prefLabels":preflabels_count,"altLabels":altlabels_count}

with open(config.datafolder+'lexonomy/lexonomy_stats.json', 'w', encoding="utf-8") as json_file:
	json.dump(lexonomy_stats, json_file, indent=2)

print('\nFinished.')
