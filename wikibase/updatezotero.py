import sys
#import lwb
import time
import requests

#changed_items = lwb.getchangeditems('Q3','2021-08-14T20:07:22Z'):

changed_items = [{'qid':'Q6123','zot':'3BR8A5PP'}]

for item in changed_items:
	zotapid = "https://api.zotero.org/groups/1892855/items/"+item['zot']
	attempts = 0
	while attempts < 5:
		try:
			attempts += 1
			r = requests.get(zotapid)
			if "200" in str(r):
				zotitem = r.json()
				print(item['zot']+': got zotitem data')
				break
			if "400" or "404" in str(r):
				print('*** Fatal error: Item ('+item['zot']+') got '+str(r)+', does not exist on Zotero. Will skip.')
				time.sleep(5)
				break
			print('Zotero API GET request failed ('+item['zot']+'), will repeat. Response was '+str(r))
			time.sleep(2)
		except Exception as ex:
			print(str(ex))
		print('Zotero API read request failed '+str(attempts)+' times.')
		time.sleep(3)

	if attempts < 5:
		version = zotitem['version']
		tags = zotitem['data']['tags']
		print(str(zotitem['data']['creators']))
	else:
		print('Abort after 5 failed attempts to get data from Zotero API.')
		sys.exit()

	authorclaims = lwb.getclaims(item['qid'],"P12")
	newauthors = {}
	for claim in authorclaims[1]["P12"]:
		guid = claim['id']
		authoritem = claim['datavalue']['value']['id']
