import csv
import json
import requests
import time
import babel_lang_codes

def getbabeltrans(bnid):

	translations = {}
	for language in babel_lang_codes.langcodemapping.keys():
		babellang = babel_lang_codes.langcodemapping[language]
		response = requests.get("https://babelnet.io/v6/getSynset?id="+bnid+"&targetLang="+babellang+"&key=2ced12ea-bd40-4ee4-9ad4-4d054c9d48e2", headers={'Accept-Encoding': 'gzip'})
		respdict_str = response.content.decode("UTF-8")
		#print(respdict_str)
		respdict = json.loads(respdict_str)
		#print(str(respdict))
		if 'senses' in respdict:
			if len(respdict['senses']) > 0:
				translations[language] = {"response":respdict_str,"lemma":respdict['senses'][0]['properties']['lemma']['lemma']}
			else:
				translations[language] = False
		else:
			print('Something went wrong with BabelNet API request...')
			return False
	return translations

# get translations from previous runs of the script
with open('D:/LexBib/terms/babeltranslations.json', 'r', encoding="utf-8") as targetfile:
	target = json.load(targetfile)

# get csv (part of google spreadsheet used for manual BabelID annotation)
with open('D:/LexBib/terms/term_bnid_status_labels.csv') as csvfile:
	termdict = csv.DictReader(csvfile)
	termlist = list(termdict)
	print(str(termlist))
	totalrows = len(termlist)
	#print(str(termdict))
	count = 0
	for row in termlist:
		count +=1
		print ('\nNow processing term '+str(count)+' of '+str(totalrows)+': '+row["term"])
		if row["term"] in target:
			print("This term has already got translations from BabelNet, skipped.")
		else:
			if row["bnid"].startswith("bn:"):
				translations = getbabeltrans(row["bnid"])
				if translations == False:
					print("BabelNet does not respond as it should, probably because we have run out of babelcoins")
					break
				else:
					target[row["term"]] = {"bn_id":row["bnid"],"status":row["status"],"prefLabel":row['prefLabel'],"altLabel":row["altLabel"]}
					target[row["term"]]["translations"] = translations
					print('*** OK. Got translations from BabelNet.')
			else:
				print('*** No BabelNet ID for this term.')
				target[row["term"]] = {"bn_id":False,"status":row["status"],"prefLabel":row['prefLabel'],"altLabel":row["altLabel"]}

with open('D:/LexBib/terms/babeltranslations.json', 'w', encoding="utf-8") as targetfile:
	json.dump(target, targetfile, indent=2)
