import xml.etree.ElementTree as xml
from xml.dom import minidom
import json
import babel_lang_codes

# get SPARQL query result (SKOS4Lexonomy) > LexBib subjects SKOS vocab
with open('D:/LexBib/terms/SKOS4Lexonomy.json', encoding="utf-8") as f:
	skos =  json.load(f, encoding="utf-8")
	subjdict = {}
	for item in skos['results']['bindings']:
		subjdict[item['subject']['value']] = {
		"broaders" : item['broaderLabels']['value'].split("@"),
		"narrowers" : item['narrowerLabels']['value'].split("@"),
		"exactMatches" : item['exactMatchLabels']['value'].split("@"),
		"related" : item['relatedLabels']['value'].split("@"),
		"definitions" : item['definitions']['value'].split("@"),
		}
#print(str(subjdict))
# get output generated with babelterms.py
with open('D:/LexBib/terms/babeltranslations.json', encoding="utf-8") as f:
	babeldict =  json.load(f, encoding="utf-8")

root = xml.Element('a3iadrmk')
processed_prefLabels = [] # this prevents from processing twice homograph term eng prefLabel (assumes that those will be exactMatches)
for subj in babeldict:
	if babeldict[subj]['prefLabel'] not in processed_prefLabels:
		print(subj)
		entry = xml.Element('entry')
		root.append(entry)
		entry.set('lexbib_id',subj)
		status_entry = xml.SubElement(entry, 'status_entry')
		term = xml.SubElement(entry, 'term')
		label_eng = xml.SubElement(term, 'label_eng')
		label_eng.text = babeldict[subj]['prefLabel']
		processed_prefLabels.append(babeldict[subj]['prefLabel'])
		if 'altLabel' in babeldict[subj]:
			altlabel_eng = xml.SubElement(term, 'altlabel_eng')
			altlabel_eng.text = babeldict[subj]['altLabel']

		for item in subjdict[subj]['broaders']:
			if len(item) > 0:
				broader = xml.SubElement(term, 'broader_eng')
				broader.text = item
		for item in subjdict[subj]['narrowers']:
			if len(item) > 0:
				narrower = xml.SubElement(term, 'narrower_eng')
				narrower.text = item

		for item in subjdict[subj]['exactMatches']:
			if len(item) > 0 and item.lower() != babeldict[subj]['prefLabel'].lower():
				exactM = xml.SubElement(term, 'exactmatch_eng')
				exactM.text = item

		for item in subjdict[subj]['related']:
			if len(item) > 0:
				related = xml.SubElement(term, 'related_eng')
				related.text = item

		for item in subjdict[subj]['definitions']:
			if len(item) > 0:
				definition = xml.SubElement(term, 'definition_eng')
				definition.text = item

		if 'bn_id' in babeldict[subj]:
			Babelnet_ID = xml.SubElement(term, 'Babelnet_ID')
			Babelnet_ID.text = babeldict[subj]['bn_id']
			Babelnet_ID.set('match_quality',babeldict[subj]['status'])

		translations = xml.SubElement(entry, 'translations')
		for lang in babel_lang_codes.langcodemapping.keys():
			if lang != "eng": # English translations are excluded here
				langelementname = "term_"+lang
				langelement = xml.SubElement(entry, langelementname)

				if 'translations' in babeldict[subj] and lang in babeldict[subj]['translations'] and babeldict[subj]['translations'][lang] != False:
					#get HIGH_QUALITY lemmata from Babel synset
					babelSenses = json.loads(babeldict[subj]['translations'][lang]['response'])['senses']
					equivs = []
					for babelSense in babelSenses:
						if babelSense['properties']['lemma']['type'] == "HIGH_QUALITY":
							equivs.append(babelSense['properties']['lemma']['lemma'].replace("_"," "))
					if len(equivs) == 0: # if there is none, try to get AUTOMATIC_TRANSLATION lemmata instead
						for babelSense in babelSenses:
							if babelSense['properties']['lemma']['type'] == "AUTOMATIC_TRANSLATION":
								equivs.append(babelSense['properties']['lemma']['lemma'].replace("_"," "))
					equivs_uniq = []
					for equiv in equivs:
						if equiv not in equivs_uniq:
							equivs_uniq.append(equiv)
					equivs_iter = iter(equivs_uniq)
					langelement.set('status',"AUTOMATIC")
					label = xml.SubElement(langelement, 'label')
					try:
						label.text = next(equivs_iter)
					except: # if no HIGH_QUALITY lemma is there, take the first listed
						label.text = babeldict[subj]['translations'][lang]['lemma'].replace("_"," ")
					while True:
						try:
							altEquiv = next(equivs_iter)
						except:
							break
						altlabel = xml.SubElement(langelement, 'altlabel')
						altlabel.text = altEquiv
				else:
					langelement.set('status',"MISSING")

tree_obj = xml.ElementTree(root)
with open('D:/LexBib/terms/lexonomy_upload.xml', "w", encoding='utf-8') as file:
	reparsed = minidom.parseString(xml.tostring(root, 'utf-8')).toprettyxml(indent = "\t")
	#print(reparsed)
	file.write(reparsed)
