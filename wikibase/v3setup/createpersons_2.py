import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv

with open(config.datafolder+'persons/lexbiblegacypersons_2.csv', 'r', encoding="utf-8") as csvfile:
	persons = csv.DictReader(csvfile)
	index = 0
	for person in persons:
		index += 1

		print('\n['+str(index)+'] '+str(person)+'\n')

		qid = person['uri']
		#statement = lwb.stringclaim(qid, "P1", person['legacyID'])
		statement = lwb.updateclaim(qid, "P101", person['given'], "string")
		statement = lwb.updateclaim(qid, "P102", person['family'], "string")
