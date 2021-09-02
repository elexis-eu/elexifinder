import config
import lwb
import csv

with open(config.datafolder+'terms/lexbiblegacycollections.csv', 'r', encoding="utf-8") as csvfile:
	collections = csv.DictReader(csvfile)

	for collection in collections:
		qid = lwb.newitemwithlabel("Q33", "en", collection['label'])
		lwb.stringclaim(qid, "P1", collection['s'])
