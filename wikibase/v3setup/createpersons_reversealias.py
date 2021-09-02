import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv

with open(config.datafolder+'persons/lexbibv3persons.csv', 'r', encoding="utf-8") as csvfile:
	persons = csv.DictReader(csvfile)
	index = 0
	for person in persons:
		index += 1

		print('\n['+str(index)+'] '+str(person)+'\n')

		qid = person['person']
		lwb.setlabel(qid,"en",person['lastName']+", "+person['givenName'], type="alias")
