import config
import lwb
import csv
import json

with open(config.datafolder+'terms/lexbiblegacytermwds.csv', 'r', encoding="utf-8") as csvfile:
	termwds = csv.DictReader(csvfile)

	for termwd in termwds:
		#print(str(lang))
		not_found = []
		print('\nWill find qid for term '+termwd['term'])
		qid = lwb.getidfromlegid("Q7", termwd['term'], onlyknown=True)
		if not qid:
			not_found.append(termwd['term'])
		else:
			statement = lwb.stringclaim(qid, "P2", termwd['wd'])
			if 'bnid' in termwd:
				if termwd['bnid'].startswith('bn:'):
					lwb.setqualifier(qid, "P2", statement, "P86", termwd['bnid'].replace("bn:",""), "string")

with open('notfoundterms.txt', "a", encoding="utf-8") as notfoundfile:
	json.dump(not_found, notfoundfile, indent=2)
