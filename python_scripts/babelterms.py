import csv
import json
import requests
import time

def getbabeltrans(bnid):
	languages = {
	"SL":"slv",
	"ES":"spa",
	"IT":"ita",
	"DE":"deu",
	"PT":"por",
	"CS":"ces",
	"ET":"est",
	"HU":"hun",
	"DA":"dan",
	"SV":"swe",
	"NO":"nor",
	"FI":"fin",
	"HR":"hrv",
	"SR":"srp",
	"LV":"lav",
	"SK":"slk",
	"PL":"pol",
	"BG":"bul",
	"RO":"ron",
	"IS":"isl",
	"BE":"bel",
	"GA":"gle",
	#"":"cnr", MONTENEGRIN NOT ON BABELNET
	"MK":"mkd",
	"RU":"rus",
	"UK":"ukr",
	"EU":"eus"
	}

	translations = {}
	for language in languages:
		response = requests.get("https://babelnet.io/v6/getSynset?id="+bnid+"&targetLang="+language+"&key=2ced12ea-bd40-4ee4-9ad4-4d054c9d48e2", headers={'Accept-Encoding': 'gzip'})
		respdict_str = response.content.decode("UTF-8")
		#print(respdict_str)
		respdict = json.loads(respdict_str)
		#print(str(respdict))
		if 'senses' in respdict:
			if len(respdict['senses']) > 0:
				translations[languages[language]] = respdict['senses'][0]['properties']['lemma']['lemma']
		else:
			print('Something went wrong with BabelNet API request...')
			return False
	return translations

with open('D:/LexBib/terms/babeltranslations.json', 'r', encoding="utf-8") as targetfile:
	target = json.load(infile)

with open('D:/LexBib/terms/term_bnid_conf.csv') as csvfile: # source file
	termdict = csv.DictReader(csvfile)
	termlist = list(termdict)
	print(str(termlist))
	totalrows = len(termlist)
	#print(str(termdict))
	count = 0
	for row in termlist:
		count +=1
		print ('Now processing term '+str(count)+' of '+str(totalrows)+': '+row["term_uri"])
		if row["term_uri"] in target:
			print("This term has already got translations from BabelNet, skipped.")
		else:
			#print(str(row))
			target[row["term_uri"]] = {"bn_id":row["bnid"],"conf":row["conf"]}
			if row["bnid"].startswith("bn:"):
				translations = getbabeltrans(row["bnid"])
				if translations = False
					print("BabelNet does not respond as it should, probably because we have run out of babelcoins")
					break
				else:
					target[row["term_uri"]]["translations"] = translations

with open('D:/LexBib/terms/babeltranslations.json', 'w', encoding="utf-8") as targetfile:
	json.dump(target, targetfile, indent=2)
