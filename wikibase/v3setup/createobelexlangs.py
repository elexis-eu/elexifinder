import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv



with open(config.datafolder+'obelex-dict/languages_wd.csv', 'r', encoding="utf-8") as csvfile:
	obelexlangs = csv.DictReader(csvfile, delimiter="\t")

	for lang in obelexlangs:
		print(str(lang))
		if not (lang['lwbqid'].startswith("Q")):
			qid = lwb.newitemwithlabel("Q8", "en", lang['wdlang'])
			statement = lwb.stringclaim(qid, "P2", lang['wdqid'])
			if len(lang['iso3']) > 0:
				statement = lwb.stringclaim(qid, "P32", lang['iso3'])
