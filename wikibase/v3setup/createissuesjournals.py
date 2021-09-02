import config
import lwb
import csv
import json

with open(config.datafolder+'journals/lexbiblegacyissues_journals.csv', 'r', encoding="utf-8") as csvfile:
	issuejournals = csv.DictReader(csvfile)

	for issuejournal in issuejournals:
		print("")
		not_found = []
		qid = lwb.getidfromlegid("Q16", issuejournal['issue'], onlyknown=True)
		if not qid:
			not_found.append({"legid":legid, "type":"issue"})
		else:
			statement = lwb.updateclaim(qid, "P5", "Q16", "item")
			statement = lwb.updateclaim(qid, "P5", "Q12", "item")
			oqid = lwb.getidfromlegid("Q20", issuejournal['journal'], onlyknown=True)
			if not oqid:
				not_found.append({"legid":issuejournal['journal'], "type":"journal"})
			else:
				statement = lwb.itemclaim(qid, "P46", oqid)

with open('notfoundissuejournals.txt', "a", encoding="utf-8") as notfoundfile:
	json.dump(not_found, notfoundfile, indent=2)
