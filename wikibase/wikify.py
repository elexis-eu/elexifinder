import config, sys, re, time, requests, json, os, traceback

def wikify(itemuri, bodytxt):
	# Event Registry "news api"
	with open(config.datafolder+'elexifinder/eventregistry_api_key.txt') as pwdfile:
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
				except Exception:
					concepts = None
					res['concepts_builderror'] = str(ex)
					print('Got error building concepts EF object: \n'+traceback.format_exc())
				itemterms = {'annotations':res['annotations'], 'concepts': concepts}
				with open(config.datafolder+'bodytxt/wikification/'+itemuri+'.json', 'w', encoding="utf-8") as jsonfile:
					json.dump(itemterms, jsonfile, indent=2)
				print('Returned wiki concepts: '+str(len(concepts))+'.')
				return itemterms
		except Exception:
			print('Error while interacting with ER API.')
			print(traceback.format_exc())
			time.sleep(2)

def update_elexifinder_indices():
	EFhost = "http://finder.elex.is"
	print('Will now update Elexifinder suggest indices...')
	res = requests.get(EFhost + "/api/v1/suggestConcepts", { "action": "updatePrefixes" })
	print(str(res))
	time.sleep(1)
	res = requests.get(EFhost + "/api/v1/suggestCategories", { "action": "updatePrefixes" })
	print(str(res))
	time.sleep(1)
	res = requests.get(EFhost + "/api/v1/suggestSources", { "action": "updatePrefixes" })
	print(str(res))
	time.sleep(1)
	res = requests.get(EFhost + "/api/v1/suggestAuthors", { "action": "updatePrefixes" })
	print(str(res))
