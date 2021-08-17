import config
import lwb
import csv
import json

with open(config.datafolder+'terms/lexbiblegacycolls.csv', 'r', encoding="utf-8") as csvfile:
	termcolls = csv.DictReader(csvfile)

	for termcoll in termcolls:
		#print(str(lang))
		not_found = []
		print('\nWill find qid for term '+termcoll['term'])
		qid = lwb.getidfromlegid("Q7", termcoll['term'], onlyknown=True)
		if not qid:
			not_found.append(termcoll['s'])
		else:
			print('Will find qid for skosColl '+termcoll['coll'])
			oqid = lwb.getidfromlegid("Q7", termcoll['coll'], onlyknown=True)
			if not oqid:
				not_found.append(termcoll['coll'])
			else:
				statement = lwb.itemclaim(qid, "P74", oqid)

with open('notfoundterms.txt', "a", encoding="utf-8") as notfoundfile:
	json.dump(not_found, notfoundfile, indent=2)
