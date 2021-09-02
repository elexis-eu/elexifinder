import xml.etree.ElementTree as xml
from xml.dom import minidom
import json
import requests
import time
import babel_lang_codes

# get Q7 SKOS Concepts
url = "https://data.lexbib.org/query/sparql?format=json&query=%23%20sparql%20query%20for%20LexDo%20Subject%20Headings%20SKOS%20vocabulary%2C%0A%23%20version%20for%20Lexonomy%20export%0A%0APREFIX%20lwb%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fqualifier%2F%3E%0A%0ASELECT%0A%3Fsubject%0A%28strafter%28str%28%3Fsubject%29%2C%22http%3A%2F%2Fdata.lexbib.org%2Fentity%2F%22%29%20as%20%3Fterm_id%29%0A%3Fbabelnet_synset%0A%3Fmatch_quality%0A%0A%3FsubjectLabel%0A%28group_concat%28distinct%20%3FsubjectAltLabel%3B%20SEPARATOR%3D%22%40%22%29%20as%20%3FsubjectAltLabels%29%0A%28group_concat%28distinct%20%3FbroaderLabel%3B%20SEPARATOR%3D%22%40%22%29%20as%20%3FbroaderLabels%29%0A%28group_concat%28distinct%20%3FnarrowerLabel%3B%20SEPARATOR%3D%22%40%22%29%20as%20%3FnarrowerLabels%29%0A%28group_concat%28distinct%20%3FcloseMatchLabel%3B%20SEPARATOR%3D%22%40%22%29%20as%20%3FcloseMatchLabels%29%0A%28group_concat%28distinct%20%3FrelatedLabel%3B%20SEPARATOR%3D%22%40%22%29%20as%20%3FrelatedLabels%29%0A%28group_concat%28distinct%20%3Fdefinition%3B%20SEPARATOR%3D%22%40%22%29%20as%20%3Fdefinitions%29%0A%0A%23%28group_concat%28BIND%28REPLACE%28str%28%3Fbroader%29%2C%20%22%5B%2F%23%5D%28%5B%5E%23%2F%5D%2B%29%24%22%2C%20%22%241%22%29%20AS%20%3Fcleanbroader%29%29%20as%20%3Fbroaders%29%0A%0A%23%28group_concat%28%3FbroaderLabel%3B%20SEPARATOR%3D%22%40%22%29%20as%20%3FbroaderLabels%29%0A%0A%0A%0A%0AWHERE%20%7B%0A%20%20%20%20%3Fsubject%20ldp%3AP5%20lwb%3AQ7%20.%0A%20%20%20%20%3Fsubject%20rdfs%3Alabel%20%3FsubjectLabel%20.%0A%20%20%20%20%20%20%20%20FILTER%20%28lang%28%3FsubjectLabel%29%3D%22en%22%29%0A%20%20%23%20%20MINUS%20%7B%3Fsubject%20ldp%3AP72%20%3Chttp%3A%2F%2Flexbib.org%2Fterms%23Term_Language%3E.%7D%0AOPTIONAL%20%7B%20%3Fsubject%20skos%3AaltLabel%20%3FsubjectAltLabel%20.%7D%0AOPTIONAL%20%7B%20%0A%20%20%20%20%20%20%20%20%20%20%20%3Fsubject%20lp%3AP86%20%3Fbabelnet_synset_statement%20.%0A%20%20%20%20%20%20%20%20%20%20%20%3Fbabelnet_synset_statement%20lps%3AP86%20%3Fbabelnet_synset%20.%0A%20%20%20%20%20%20%20%20%20%20%20%3Fbabelnet_synset_statement%20lpq%3AP87%20%3Fmatch_quality%20.%0A%20%20%20%20%7D%0A%20%20%20%20%20%20%20%0AOPTIONAL%20%7B%0A%20%20%20%20%3Fsubject%20ldp%3AP72%20%3Fbroader%20.%0A%20%20%20%20%3Fbroader%20rdfs%3Alabel%20%3FbroaderLabel.%0A%20%20%20%20%20%20%20%20FILTER%20%28lang%28%3FbroaderLabel%29%3D%22en%22%29%0A%20%20%20%20%7D%0AOPTIONAL%20%7B%0A%20%20%20%20%3Fnarrower%20ldp%3AP72%20%3Fsubject%20.%0A%20%20%20%20%3Fnarrower%20rdfs%3Alabel%20%3FnarrowerLabel.%0A%20%20%20%20%20%20%20%20FILTER%20%28lang%28%3FnarrowerLabel%29%3D%22en%22%29%0A%20%20%20%20%7D%0AOPTIONAL%20%7B%20%7B%0A%20%20%20%20%3Fsubject%20ldp%3AP77%20%3FcloseMatch%20.%0A%20%20%20%20%3FcloseMatch%20rdfs%3Alabel%20%3FcloseMatchLabel.%0A%20%20%20%20%20%20%20%20FILTER%20%28lang%28%3FcloseMatchLabel%29%3D%22en%22%29%0A%20%20%20%7D%20UNION%20%7B%0A%20%20%20%20%3FcloseMatch%20ldp%3AP77%20%3Fsubject%20.%0A%20%20%20%20%3FcloseMatch%20rdfs%3Alabel%20%3FcloseMatchLabel.%0A%20%20%20%20%20%20%20%20FILTER%20%28lang%28%3FcloseMatchLabel%29%3D%22en%22%29%0A%20%20%20%7D%20%7D%0AOPTIONAL%20%7B%20%7B%0A%20%20%20%20%3Fsubject%20ldp%3AP76%20%3Frelated%20.%0A%20%20%20%20%3Frelated%20rdfs%3Alabel%20%3FrelatedLabel.%0A%20%20%20%20%20%20%20%20FILTER%20%28lang%28%3FrelatedLabel%29%3D%22en%22%29%0A%20%20%20%20%7D%20UNION%20%7B%0A%20%20%20%20%3Frelated%20ldp%3AP76%20%3Fsubject%20.%0A%20%20%20%20%3Frelated%20rdfs%3Alabel%20%3FrelatedLabel.%0A%20%20%20%20%20%20%20%20FILTER%20%28lang%28%3FrelatedLabel%29%3D%22en%22%29%0A%20%20%20%20%7D%20%7D%0AOPTIONAL%20%7B%0A%20%20%20%20%3Fsubject%20ldp%3AP80%20%3Fdefinition%20.%0A%20%20%20%20%7D%0A%7D%0AGROUP%20BY%20%3FsubjectLabel%20%3Fterm_id%20%3Fbabelnet_synset%20%3Fmatch_quality%20%3Fsubject%20%3FsubjectAltLabels%20%3FbroaderLabels%20%3FnarrowerLabels%20%3FcloseMatchLabels%20%3FrelatedLabels%20%3Fdefinitions%0A%23limit%2010"
done = False
while (not done):
	try:
		r = requests.get(url)
		skos = r.json()
	except Exception as ex:
		print('Error: SPARQL request failed: '+str(ex))
		time.sleep(2)
		continue
	done = True

	subjdict = {}
	for item in skos['results']['bindings']:
		if len(item['broaderLabels']['value'] + item['closeMatchLabels']['value'] + item['relatedLabels']['value']) > 1: # at least one of these 3 rels

			lwbqid = item['term_id']['value']
			if lwbqid not in subjdict:
				subjdict[lwbqid] = {}
				prefLabel = item['subjectLabel']['value'].lower()
			subjdict[lwbqid]["prefLabel"] = prefLabel
			subjdict[lwbqid]["altLabels"] = item['subjectAltLabels']['value'].split("@")
			subjdict[lwbqid]["broaders"] = item['broaderLabels']['value'].split("@")
			subjdict[lwbqid]["narrowers"] = item['narrowerLabels']['value'].split("@")
			subjdict[lwbqid]["closeMatches"] = item['closeMatchLabels']['value'].split("@")
			subjdict[lwbqid]["related"] = item['relatedLabels']['value'].split("@")
			subjdict[lwbqid]["definitions"] = item['definitions']['value'].split("@")

			if "bn_id" not in subjdict[lwbqid]:
				subjdict[lwbqid]["bn_id"] = []
			if 'babelnet_synset' in item:
				bn_id = item['babelnet_synset']['value']
			else:
				bn_id = ""
			if 'match_quality' in item:
				match_qual = item['match_quality']['value']
			else:
				match_qual = "0"
			subjdict[lwbqid]["bn_id"].append({"bn_id":bn_id,"match_quality":match_qual})

print(str(subjdict))
#time.sleep(5)
# get output generated with babelterms.py
with open('D:/LexBib/terms/babeltranslations_lwbqid.json', encoding="utf-8") as f:
	babeldict =  json.load(f, encoding="utf-8")

root = xml.Element('a3iadrmk')

notranslist = []
for subj in subjdict:
	if subj not in babeldict: # terms that not have been translated in babelnet
		notranslist.append(subjdict[subj]['prefLabel'])
	else:
		print(subj)
		entry = xml.Element('entry')
		root.append(entry)
		entry.set('lexbib_id',subj)
		status_entry = xml.SubElement(entry, 'status_entry')
		term = xml.SubElement(entry, 'term')

		for item in subjdict[subj]['bn_id']:
			Babelnet_ID = xml.SubElement(entry, 'Babelnet_ID')
			Babelnet_ID.text = item["bn_id"]
			Babelnet_ID.set('match_quality',item["match_quality"])

		label_eng = xml.SubElement(term, 'label_eng')
		label_eng.text = subjdict[subj]['prefLabel']
		#print(subjdict[subj]['prefLabel'])
		#time.sleep(1)

		for item in subjdict[subj]['altLabels']:
			if item.lower() != subjdict[subj]['prefLabel']: # due to upper/lower case initials, there may be duplicate labels (if case insensitive)
				altlabel_eng = xml.SubElement(term, 'altlabel_eng')
				altlabel_eng.text = item.lower()

		for item in subjdict[subj]['broaders']:
			if len(item) > 0:
				broader = xml.SubElement(term, 'broader_eng')
				broader.text = item
		for item in subjdict[subj]['narrowers']:
			if len(item) > 0:
				narrower = xml.SubElement(term, 'narrower_eng')
				narrower.text = item

		for item in subjdict[subj]['closeMatches']:
			if len(item) > 0:
				closeM = xml.SubElement(term, 'closematch_eng')
				closeM.text = item

		for item in subjdict[subj]['related']:
			if len(item) > 0:
				related = xml.SubElement(term, 'related_eng')
				related.text = item

		for item in subjdict[subj]['definitions']:
			if len(item) > 0:
				definition = xml.SubElement(term, 'definition_eng')
				definition.text = item

		translations = xml.SubElement(entry, 'translations')

		for lang in babel_lang_codes.langcodemapping.keys():
			if lang != "eng": # English translations are excluded here
				langelementname = "term_"+lang
				langelement = xml.SubElement(translations, langelementname)

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

#print(str(root))

#tree_obj = xml.ElementTree(root)
treestring = xml.tostring(root, encoding="unicode")
#print(str(treestring))
#print(str(tree_obj))
with open('D:/LexBib/terms/lexonomy_upload_new.xml', "w", encoding="utf-8") as file:
	reparsed = minidom.parseString(treestring).toprettyxml(indent = "\t")
	#print(str(reparsed))
	file.write(reparsed)

with open('D:/LexBib/terms/terms_without_trans.txt', 'w', encoding="utf-8") as file:
	for item in notranslist:
		file.write(item+"\n")
