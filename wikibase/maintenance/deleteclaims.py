import csv
import lwb
import config


with open(config.datafolder+'newwikibase/del.csv', 'r', encoding="utf-8") as csvfile:
	dellist = csv.DictReader(csvfile)

	for row in dellist:
		lwb.removeclaim(row['del'])
