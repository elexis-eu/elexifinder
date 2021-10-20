import sys
import lwb
import config
import time
import re
import requests
from pyzotero import zotero
pyzot = zotero.Zotero(1892855,'group',config.zotero_api_key)
#changed_items = lwb.getchangeditems('Q3','2021-08-14T20:07:22Z'):

zotitems_to_update = pyzot.items(tag=":update_from_lwb")
for item in zotitems_to_update:
	#print(str(item))
	if ('archiveLocation' not in item['data']) or (not item['data']['archiveLocation'].startswith("http://lexbib.elex.is/entity/Q")):
		print('Error: trying to update item without valid link to LWB. Exit.')
		sys.exit()
	qid = re.search(r'http://lexbib.elex.is/entity/(Q\d+)', item['data']['archiveLocation']).group(1)
	print('Got Zotitem data with LWB link. Will update item '+qid+'...')

	authorclaims = lwb.getclaims(qid,"P12")
	print('Got author claims')
	time.sleep(0.1)
	updatedauthors = {}
	if "P12" in authorclaims[1]:
		for claim in authorclaims[1]["P12"]:
			#guid = claim['id']
			authoritem = claim['mainsnak']['datavalue']['value']['id']
			authorlistpos = claim['qualifiers']['P33'][0]['datavalue']['value']
			lastnameclaims = lwb.getclaims(authoritem,"P102")
			#print(str(lastnameclaims))
			lastname = lastnameclaims[1]["P102"][0]['mainsnak']['datavalue']['value']
			print('Found last name: '+lastname)
			time.sleep(0.1)
			firstnameclaims = lwb.getclaims(authoritem,"P101")
			firstname = firstnameclaims[1]["P101"][0]['mainsnak']['datavalue']['value']
			print('Found first name: '+firstname)
			time.sleep(0.1)
			updatedauthors[authorlistpos] = {'creatorType':'author',
										'firstName': firstname,
										'lastName': lastname}
	newauthorlist = []
	for index in range(len(updatedauthors)):
		newauthorlist.append(updatedauthors[str(index+1)])

	item['data']['creators'] = newauthorlist
	pyzot.update_item(item)
	print('Successfully written to Zotero. Author info is:\n'+str(newauthorlist))
	time.sleep(0.2)
