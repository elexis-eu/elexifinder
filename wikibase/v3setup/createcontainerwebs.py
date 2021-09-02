import config
import lwb
import csv

with open(config.datafolder+'containers/lexbiblegacycontainerwebs.csv', 'r', encoding="utf-8") as csvfile:
	containerwebs = csv.DictReader(csvfile)

	for containerweb in containerwebs:
		#print(str(lang))

		qid = lwb.getidfromlegid("Q12", containerweb['uri'])
		statement = lwb.updateclaim(qid, "P44", containerweb['web'], "url")
