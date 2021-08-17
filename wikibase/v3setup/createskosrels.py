import config
import lwb
import csv
import json

with open(config.datafolder+'terms/lexbiblegacyskosrels.csv', 'r', encoding="utf-8") as csvfile:
	skosrels = csv.DictReader(csvfile)

	for skosrel in skosrels:
		#print(str(lang))
		not_found = []
		qid = lwb.getidfromlegid("Q7", skosrel['s'], onlyknown=True)
		if not qid:
			not_found.append(skosrel['s'])
		else:
			oqid = lwb.getidfromlegid("Q7", skosrel['o'], onlyknown=True)
			if not oqid:
				not_found.append(skosrel['o'])
			else:
				statement = lwb.itemclaim(qid, skosrel['edge'], oqid)

with open('notfoundskosrels.txt', "a", encoding="utf-8") as notfoundfile:
	json.dump(not_found, notfoundfile, indent=2)
