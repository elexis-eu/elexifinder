import config
import lwb
import csv

with open(config.datafolder+'journals/lexbiblegacyjournals.csv', 'r', encoding="utf-8") as csvfile:
	journals = csv.DictReader(csvfile)

	for journal in journals:
		#print(str(lang))

		qid = lwb.newitemwithlabel("Q20", "en", journal['label'])
		statement = lwb.stringclaim(qid, "P1", journal['journal'])
		statement = lwb.stringclaim(qid, "P2", journal['wdid'])
