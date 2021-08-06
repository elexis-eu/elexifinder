import config
import lwb
import csv

with open(config.datafolder+'persons/lexbiblegacypersons.csv', 'r', encoding="utf-8") as csvfile:
	persons = csv.DictReader(csvfile)
	index = 0
	for person in persons:
		index += 1

		print('\n['+str(index)+'] '+str(person)+'\n')

		qid = lwb.newitemwithlabel("Q5", "en", person['personLabel'])
		statement = lwb.stringclaim(qid, "P1", person['legacyID'])
		statement = lwb.stringclaim(qid, "P40", person['firstname'])
		statement = lwb.stringclaim(qid, "P41", person['lastname'])
