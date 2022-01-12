import sys, re, time, requests, json, os

def wikify(itemuri, bodytxt):
	# Event Registry "news api"
	with open('D:/LexBib/elexifinder/eventregistry_api_key.txt') as pwdfile:
		ERapiKey = pwdfile.read()
	print('Will upload BibItem '+itemuri+' to Event Registry.')
	params = {
	    "text": bodytxt,
	    "apiKey": ERapiKey
	}
	done = False
	attempts = 0
	while (not done):
		attempts += 1
		if attempts > 4:
			print('Event Registry request failed 5 times. Abort.')
			sys.exit()
		try:
			res = requests.get("http://analytics.eventregistry.org/api/v1/annotate", json = params).json()
			#print(res.json())
			if 'annotations' in res:
				try:
					concepts = []
					for term in res['annotations']:
						concept = {}
						if 'wikiDataItemId' in term:
							concept['uri'] = "wd:"+term['wikiDataItemId']
						else:
							concept['uri'] = "enwiki:"+term['url'].replace("http://en.wikipedia.org/wiki/","")
						wikipagetitle = term['title']
						concept['label'] = re.sub(r' \([^\)]+\)', '', wikipagetitle) # delete disambiguator in title, e.g. "Taxonomy (Biology)"
						concept['type'] = term['type']
						concept['wgt'] = term['wgt']
						concepts.append(concept)
						#print('Successfully wrote EF object')
				except Exception as ex:
					concepts = None
					res['concepts_builderror'] = str(ex)
					print('Got error building concepts EF object: '+str(ex))
				itemterms = {'annotations':res['annotations'], 'concepts': concepts}
				with open('D:/LexBib/bodytxt/wikification/'+itemuri+'.json', 'w', encoding="utf-8") as jsonfile:
					json.dump(itemterms, jsonfile, indent=2)
				return itemterms
		except Exception as ex:
			print('Error while interacting with ER API.')
			print(str(ex))
			time.sleep(2)
