import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv

with open(config.datafolder+'containers/lexbiblegacycontainershorttitles.csv', 'r', encoding="utf-8") as csvfile:
	containershorttitles = csv.DictReader(csvfile)

	for containershorttitle in containershorttitles:
		#print(str(lang))

		qid = lwb.getidfromlegid("Q12", containershorttitle['container'])
		statement = lwb.updateclaim(qid, "P97", containershorttitle['st'], "string")
