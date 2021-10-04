import lxml
from xml.etree import ElementTree
import re
import json
import time
import csv

with open('D:/LexBib/mappings/lwb_wd.jsonl', encoding="utf-8") as f:
	mappings = f.read().split('\n')
	count = 0
	wd_lwb = {}
	for mapping in mappings:
		count += 1
		if mapping != "":
			try:
				mappingjson = json.loads(mapping)
				#print(mapping)
				wd_lwb[mappingjson['wdid']] = mappingjson['lwbid']
			except Exception as ex:
				print('Found unparsable mapping json in lwb_wd.jsonl line ['+str(count)+']: '+mapping)
				print(str(ex))
				pass

with open('D:/LexBib/obelex-dict/languages_wd.csv', 'r', encoding="utf-8") as csvfile:
	obelexlangs = csv.DictReader(csvfile, delimiter="\t")
	obelexlangnames = {}
	for lang in obelexlangs:
		obelexlangnames[lang['obelexlang']] = wd_lwb[lang['wdqid']]

with open('D:/LexBib/obelex-dict/dictypes_lwb.csv', 'r', encoding="utf-8") as csvfile:
	obelextypes = csv.DictReader(csvfile, delimiter="\t")
	obelextypenames = {}
	for type in obelextypes:
		obelextypenames[type['label']] = type['lwb_qid']

resultlist = []
dictypes = []
languages = {'langs':[],'vars':{}}
portals = {}
tree = ElementTree.parse('D:/LexBib/obelex-dict/exported.xml')
obelexdict = tree.getroot()
for dictionary in obelexdict:
	result = {'lwb_lang':[],'lwb_type':[]}

	for category in dictionary:

		if category.tag == "langs":
			result['langs'] = []
			for lang in category:
				en = lang.findall('name_eng')[0].text.strip()
				if "Variety:" in en:
					print(en)
					extract = re.search(r'^([\w \-]*) Variety: ?([\w \-]*)', en)
					en = extract.group(1)
					variety = {'lang': en,'var': extract.group(2)}
					if variety['lang'] not in languages['vars']:
						languages['vars'][variety['lang']] = [variety['var']]
					else:
						if variety['var'] not in languages['vars'][variety['lang']]:
							languages['vars'][variety['lang']].append(variety['var'])
				de = lang.findall('name_ger')[0].text.strip()
				result['langs'].append({
				"en":en,
				"de":de,
				})
				if en not in languages['langs']:
					languages['langs'].append(en)
				if en in obelexlangnames:
					result['lwb_lang'].append(obelexlangnames[en])
		elif category.tag == "portal_name":
			portal = category.text
			result["portal_name"] = portal
			if portal not in portals:
				portals[portal] = 1
			else:
				portals[portal] += 1
		elif category.tag == "type_english":
			type = category.text
			result["type"] = type
			#if "[" in type and "]" in type: # type contains a domain indication in [] brackets
			domain = re.search(r'([^\[]+) \[([^\]]+)\]',type)
			if domain:
				result['type'] = domain.group(1)
				domain = domain.group(2)
				result['domain'] = domain
				print(domain)
			if type not in dictypes:
				dictypes.append(type)
			result['lwb_type'].append(obelextypenames[result['type']])
		else:
			result[category.tag] = category.text

	#print(str(result))
	resultlist.append(result)

with open('D:/LexBib/obelex-dict/obelex-parsed.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(resultlist, jsonfile, indent=2)
with open('D:/LexBib/obelex-dict/obelex-types.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(dictypes, jsonfile, indent=2)
with open('D:/LexBib/obelex-dict/obelex-languages.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(languages, jsonfile, indent=2)
with open('D:/LexBib/obelex-dict/obelex-portals.json', 'w', encoding="utf-8") as jsonfile:
	json.dump(portals, jsonfile, indent=2)
