import config
import lwb
import csv
import json

with open(config.datafolder+'terms/lexbiblegacytermaltlabels.csv', 'r', encoding="utf-8") as csvfile:
	altlabels = csv.DictReader(csvfile)

	for altlabel in altlabels:
		#print(str(lang))
		not_found = []
		qid = lwb.getidfromlegid("Q7", altlabel['term'], onlyknown=True)
		if not qid:
			not_found.append(legid)
		labelset = lwb.setlabel(qid, "en", altlabel['altLabel'], type="alias")
with open('notfoundpersons.txt', "a", encoding="utf-8") as notfoundfile:
	json.dump(not_found, notfoundfile, indent=2)
