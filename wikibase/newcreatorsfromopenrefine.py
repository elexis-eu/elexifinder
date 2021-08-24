import csv
import json
import re
import config
import lwb
import time

with open(config.datafolder+'newwikibase/creators4openrefine-csv.csv', encoding="utf-8") as f:
	data = csv.DictReader(f)

	#statement_id_re = re.compile(r'statement\/(Q\d+)\-(.*)')
	count = 1
	for item in data:
		print('\nItem ['+str(count)+'] of '+str(len(data))+':')
		bibItem = item['bibItem'].replace("http://lexbib.elex.is/entity/","")
		print('BibItem is '+bibItem+'.')
		creatorstatement = re.search(r'statement/(Q.*)', item['creatorstatement']).group(1)
		print('CreatorStatement is '+creatorstatement+'.')
		if 'Qid' in item and item['Qid'].startswith("Q"):
			creatorqid = item['Qid']
			lwb.setclaimvalue(creatorstatement, creatorqid, "item")
			creatoritemlabel = lwb.getlabel(creatorqid,"en")
			creatoritemaliaslist = lwb.getaliases(creatorqid,"en")
			if (item['fullName'] != creatoritemlabel) and (item['fullName'] not in creatoritemaliaslist):
				print('This is a new name variant for '+creatorqid+': '+item['fullName'])
				lwb.setlabel(creatorqid,"en",item['fullName'],type="alias")
		else:
			creatorqid = lwb.newitemwithlabel("Q5","en",item['fullName'])
			lwb.stringclaim(creatorqid,"P101",item['givenName'])
			lwb.stringclaim(creatorqid,"P102",item['lastName'])
			lwb.setlabel(creatorqid,"en",item['lastName']+", "+item['givenName'], type="alias")
			lwb.setclaimvalue(creatorstatement, creatorqid, "item")
		count +=1
		time.sleep(1)
