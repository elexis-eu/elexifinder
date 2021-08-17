import config
import lwb
import csv
import json

with open(config.datafolder+'terms/lexbiblegacytermdefs.csv', 'r', encoding="utf-8") as csvfile:
	termdefs = csv.DictReader(csvfile)

	for termdef in termdefs:
		#print(str(lang))
		not_found = []
		print('\nWill find qid for term '+termdef['term'])
		qid = lwb.getidfromlegid("Q7", termdef['term'], onlyknown=True)
		if not qid:
			not_found.append(termdef['term'])
		else:
			if not termdef['def'].startswith('"['):
				statement = lwb.updateclaim(qid, "P80", termdef['def'].replace('"',''), "string")
			if 'wdr' in termdef:
				if termdef['wdr'].startswith('http://www.wikidata.org/entity/'):
					lwb.setqualifier(qid, "P80", statement, "P2", termdef['wdr'].replace("http://www.wikidata.org/entity/",""), "string")
			if 'v1r' in termdef:
				if termdef['v1r'] != "":
					lwb.setqualifier(qid, "P80", statement, "P106", termdef['v1r'], "string")

with open('notfoundterms.txt', "a", encoding="utf-8") as notfoundfile:
	json.dump(not_found, notfoundfile, indent=2)
