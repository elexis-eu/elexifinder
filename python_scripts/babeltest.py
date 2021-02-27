import requests
import json

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
		translations[languages[language]] = respdict['senses'][0]['properties']['fullLemma']
	return translations
