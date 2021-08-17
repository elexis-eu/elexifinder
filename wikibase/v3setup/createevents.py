import config
import lwb
import csv

with open(config.datafolder+'events/lexbiblegacyevents.csv', 'r', encoding="utf-8") as csvfile:
	events = csv.DictReader(csvfile)

	for event in events:
		print('\n'+str(event)+'\n')

		qid = lwb.newitemwithlabel("Q6", "en", event['label'])
		#statement = lwb.stringclaim(qid, "P1", event['LexBibURI'])
		if len(event['WikidataURI']) > 1:
			statement = lwb.stringclaim(qid, "P2", event['WikidataURI'])
		placeqid = lwb.wdid2lwbid(event['place'])
		if placeqid:
			statement = lwb.updateclaim(qid, "P10", placeqid, "item")
