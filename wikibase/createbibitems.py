import config
import lwb
import csv

with open(config.datafolder+'newwikibase/legacybibitems.csv', 'r', encoding="utf-8") as csvfile:
	bibitems = csv.DictReader(csvfile)
	count = 0
	for bibitem in bibitems:
		if bibitem['bibItem'] not in lwb.legacyID:
			count += 1
			print('\n['+str(count)+'] '+str(bibitem)+'\n')

			qid = lwb.newitemwithlabel("Q3", "en", bibitem['label'])
			statement = lwb.stringclaim(qid, "P1", bibitem['bibItem'])
