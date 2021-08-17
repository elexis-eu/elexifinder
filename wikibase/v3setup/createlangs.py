import config
import lwb
import csv

existinglangs = [
"eng",
"afr",
"dan",
"deu",
"fra",
"nor",
"slv",
"spa",
"swe",
"ita",
"nno",
"por",
"rus",
"nld",
"nob",
"cat",
"ell",
"eus",
"sme",
"fry",
"bel",
"fin",
"hrv"
]

with open(config.datafolder+'languages/wdcodelangs.csv', 'r', encoding="utf-8") as csvfile:
	wdlangs = csv.DictReader(csvfile)

	for lang in wdlangs:
		#print(str(lang))
		if lang['iso3code'] not in existinglangs:
			qid = lwb.newitemwithlabel("Q8", "en", lang['langLabel'])
			statement = lwb.stringclaim(qid, "P2", lang['wdid'])
			statement = lwb.stringclaim(qid, "P32", lang['iso3code'])
			statement = lwb.stringclaim(qid, "P43", lang['wikilangcode'])
