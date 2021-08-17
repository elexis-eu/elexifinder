import config
import lwb
import csv
import json

with open(config.datafolder+'babelnet/lexbiblegacybnids.csv', 'r', encoding="utf-8") as csvfile:
	bnids = csv.DictReader(csvfile)

	for bnid in bnids:
		#print(str(lang))
		not_found = []
		qid = lwb.getidfromlegid("Q7", bnid['term'], onlyknown=True)
		if not qid:
			not_found.append(bnid['term'])
		else:
			statement = lwb.updateclaim(qid, "P86", bnid['bnid'], "string")
			lwb.setqualifier(qid,"P86",statement,"P87",bnid['mcf'],"string")

with open('notfoundterms.txt', "a", encoding="utf-8") as notfoundfile:
	json.dump(not_found, notfoundfile, indent=2)
