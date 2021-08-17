import config
import lwb
import csv

with open(config.datafolder+'places/lexbiblegacyplaces.csv', 'r', encoding="utf-8") as csvfile:
	places = csv.DictReader(csvfile)

	for place in places:
		#print(str(lang))

		qid = lwb.newitemwithlabel("Q9", "en", place['placeLabel'])
		statement = lwb.stringclaim(qid, "P1", place['legacyID'])
		statement = lwb.stringclaim(qid, "P2", place['wdid'])
		statement = lwb.stringclaim(qid, "P66", place['wppage'])
