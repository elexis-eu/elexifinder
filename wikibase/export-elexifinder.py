## produces dataset for ingestion by Event Registry software (http://finder.elex.is installation)

import re
import json
import os
import csv
import time
import sparql
import requests
from datetime import datetime
import shutil
import sys, traceback
sys.path.insert(1, os.path.realpath(os.path.pardir))
from elexifinder import collection_images
import wikify, config


# items to export

print('Will now get a list of all bibitems that have P85 Elexifinder collection...')

url = "https://lexbib.elex.is/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttps%3A%2F%2Flexbib.elex.is%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttps%3A%2F%2Flexbib.elex.is%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttps%3A%2F%2Flexbib.elex.is%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttps%3A%2F%2Flexbib.elex.is%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttps%3A%2F%2Flexbib.elex.is%2Fprop%2Fqualifier%2F%3E%0APREFIX%20lpr%3A%20%3Chttps%3A%2F%2Flexbib.elex.is%2Fprop%2Freference%2F%3E%0APREFIX%20lno%3A%20%3Chttps%3A%2F%2Flexbib.elex.is%2Fprop%2Fnovalue%2F%3E%0A%0Aselect%20%3FbibItem%0A%0Awhere%20%7B%0A%20%20%3FbibItem%20ldp%3AP85%20%3Fcollection%20.%0A%20%20%7D"
done = False
while (not done):
	try:
		r = requests.get(url)
		bindings = r.json()['results']['bindings']
	except Exception as ex:
		print('Error: SPARQL request failed: '+str(ex))
		time.sleep(2)
		continue
	done = True
#print(str(bindings))

export_items = []
for binding in bindings:
	export_items.append(binding['bibItem']['value'].replace("https://lexbib.elex.is/entity/",""))
print('Found '+str(len(export_items))+' items.\n')
time.sleep(1)


# export_items = """Q6059
# Q15467
# Q9054
# Q13618
# Q10752
# Q13279
# Q12734
# Q8693
# Q12270
# Q11845
# Q15742
# Q11229""".split("\n")

# pubTime
pubTime = str(datetime.now()).replace(' ','T')[0:22]
print(pubTime)

# Elexifinder API key
with open(config.datafolder+'elexifinder/elexifinder_api_key.txt') as pwdfile:
	EFapiKey = pwdfile.read()
# Event Registry "news api" key
with open(config.datafolder+'elexifinder/eventregistry_api_key.txt') as pwdfile:
	ERapiKey = pwdfile.read()
# with open(config.datafolder+'bodytxt/foundwikiterms.json', "r", encoding="utf-8") as jsonfile:
# 	wikiterms = json.load(jsonfile)
wikidir = os.listdir(config.datafolder+'bodytxt/wikification')
EFhost = "http://finder.elex.is"

# get donelist
with open(config.datafolder+'elexifinder/export_last_donelist.txt', 'r', encoding="utf-8") as txt_file:
	donelist = txt_file.read().split("\n")

# write to list of missing bodytxt items
def add_missing_list(itemuri):
	with open(config.datafolder+'/elexifinder/missing_bodytxts.txt', 'a', encoding="utf-8") as failed_list:
		failed_list.write(itemuri+'\n')

def get_item_data(itemuri):
	query = """
	PREFIX lwb: <https://lexbib.elex.is/entity/>
PREFIX ldp: <https://lexbib.elex.is/prop/direct/>
PREFIX lp: <https://lexbib.elex.is/prop/>
PREFIX lps: <https://lexbib.elex.is/prop/statement/>
PREFIX lpq: <https://lexbib.elex.is/prop/qualifier/>
PREFIX lpr: <https://lexbib.elex.is/prop/reference/>
PREFIX lno: <https://lexbib.elex.is/prop/novalue/>

SELECT
?bibItem
(CONCAT('[ ',GROUP_CONCAT(?authordata; separator=", "),' ]') AS ?authorsJson)
?collection
?title
?articleTM
(sample(?zotItem) as ?zotItemUri)
?publang
#(group_concat(distinct strafter(str(?pdffile),"http://lexbib.org/zotero/");separator="@") as ?pdffiles)
#(group_concat(distinct strafter(str(?txtfile),"http://lexbib.org/zotero/");separator="@") as ?txtfiles)
(sample(?fullTextUrls) as ?fullTextUrl)
(sample(?containerFullTextUrl) as ?containerUrl)
#(sample(?containerUrl) as ?containerUrl)
(sample(?containerShortTitle) as ?containerShortTitle)
?authorLoc
?articleLoc
?articleLocLabel
?articleCountryLabel
(sample(strafter(str(?p100),"https://lexbib.elex.is/entity/")) as ?bibitemtype)

where {
  BIND(lwb:"""+itemuri+""" as ?bibItem)
  ?bibItem lp:P12 ?authorstatement .
  ?authorstatement lps:P12 ?authornode .
  ?authorstatement lpq:P33 ?listpos .
  ?authornode rdfs:label ?authorlabel .
 BIND ( concat ('{"uri": "', strafter(str(?authornode),"https://lexbib.elex.is/entity/"),
                '", "name": "', ?authorlabel, '", "listpos": "', ?listpos, '"}') as ?authordata )
  ?bibItem ldp:P5 lwb:Q3 .
  ?bibItem ldp:P85 ?collection .
  ?bibItem ldp:P6 ?title .
  ?bibItem ldp:P100 ?p100 . # ?p100 rdfs:label ?p100label . filter(lang(?p100label)="en")
  ?bibItem ldp:P15 ?articleTM .
  ?bibItem ldp:P11 ?langItem . ?langItem ldp:P32 ?publang .
  ?bibItem lp:P16 ?zotstatement.
  ?zotstatement lps:P16 ?zotItem.
#  OPTIONAL {?zotstatement lpq:P70 ?pdffile .}
#  OPTIONAL {?zotstatement lpq:P71 ?txtfile .}
  OPTIONAL {?bibItem ldp:P21|ldp:P113|ldp:P112 ?fullTextUrls .}
  OPTIONAL {?bibItem ldp:P29 ?auLocUri . ?auLocUri ldp:P66 ?authorLoc .}
  OPTIONAL {?bibItem ldp:P9 ?containerUri .
  OPTIONAL {?containerUri ldp:P21|ldp:P111 ?containerFullTextUrl .}
  OPTIONAL {?containerUri ldp:P97 ?containerShortTitle .}
  OPTIONAL {?bibItem ldp:P36 ?event. ?event ldp:P50 ?eventloc.
            ?eventloc ldp:P66 ?articleLoc; rdfs:label ?articleLocLabel . filter(lang(?articleLocLabel)="en")
            ?eventloc ldp:P65 ?articleCountry. ?articleCountry rdfs:label ?articleCountryLabel. filter(lang(?articleCountryLabel)="en") }


}
}GROUP BY
 ?bibItem
 ?authorsJson
 ?collection
 ?title
 ?articleTM
 ?zotItemUri
 ?publang
# ?pdffiles
# ?txtfiles
 ?fullTextUrl
 ?containerUrl
 #?containerUrl
 ?containerShortTitle
 ?authorLoc
 ?articleLoc
 ?articleLocLabel
 ?articleCountryLabel
 ?bibitemtype
limit 10
	"""
	url = "https://lexbib.elex.is/query/sparql"
	print("Waiting for SPARQL to deliver item data...")
	sparqlresults = sparql.query(url,query)
	for row in sparqlresults:
		itemdata = sparql.unpack_row(row, convert=None, convert_type={})
		#print(str(itemdata))
		print('Got item data.')
		return itemdata

# load subject list
with open(config.datafolder+'terms/elexifinder-catlabels-3level.csv', encoding="utf-8") as csvfile:
	catlabels_csv = csv.DictReader(csvfile)
	termlabels = {}
	catlabels = {}
	labellist = []
	for row in catlabels_csv:
		termqid = row['term'].replace("https://lexbib.elex.is/entity/","")
		#erlabel = re.search(r'[\w ]+$',row['ercat']).group(0)
		termlabels[termqid] = row['termLabel']
		labellist.append(row['termLabel'].lower())
		catlabels[termqid] = {"uri":row['ercat'].replace(" ","_"),"label":row['ercat'].replace("Lexicography/","")}


#print(str(catlabels))

with open(config.datafolder+'bodytxt/foundterms_last.json', encoding="utf-8") as jsonfile:
	foundterms = json.load(jsonfile)

with open(config.datafolder+'bodytxt/bodytxt_collection.json', encoding="utf-8") as jsonfile:
	bodytxts = json.load(jsonfile)

elexifinder = []
itemcount = 0

for itemuri in export_items:

	itemcount += 1
	print('\nNow processing item '+str(itemcount)+' of '+str(len(export_items))+': '+itemuri)

	if itemuri in donelist:
		print(itemuri+" is in donelist, skipped.")
		continue

	conceptlabels = []
	target = {'uri': itemuri}

	# get term indexation
	target['concepts'] = []
	target['categories'] = []
	if itemuri not in foundterms:
		print('Term indexation not found for item '+itemuri)
		time.sleep(1)
	else:
		print('Found lexvoc term indexation data.')
		for foundterm in foundterms[itemuri]:
			if termlabels[foundterm].lower() not in conceptlabels: # avoids double listing of homograph term labels
				target['concepts'].append({
				"uri": "lexbib:"+foundterm,
				"label": termlabels[foundterm],
				"type": "person",
				"wgt": 1
				})
				conceptlabels.append(termlabels[foundterm].lower())
			if foundterm not in catlabels:
				print('er-catlabel not found. Must be a redirect uri.')
				time.sleep(1)
				continue
			if catlabels[foundterm] not in target['categories']:
				target['categories'].append(catlabels[foundterm])
				#print('Term found in this item: '+str(catlabels[foundterm]))




	# get item data
	itemdata = get_item_data(itemuri)
	if itemdata == None:
		print('ERROR: Got no itemdata (missing result). There is something wrong with '+itemuri+'.')
		with open(config.datafolder+'elexifinder/upload-errors.txt', 'a', encoding="utf-8") as errorfile:
			errorfile.write(itemuri+"\t"+str(datetime.now()).replace(' ','T')[0:22]+"\tItemdata SPARQL failed\n")
		continue
	target['pubTm'] = pubTime
	target['version'] = 3
	target['details'] = {'collection_version': 3}
	if itemdata[1]:
		target['authors'] = json.loads(itemdata[1])
	else:
		print('Authors JSON missing.')
	if itemdata[3]:
		target['title'] = itemdata[3]
	else:
		print('Title missing.')
	if itemdata[4]:
		target['articleTm'] = str(itemdata[4])[0:22].replace(' ','T')
	else:
		print('Publication date missing.')

	# target['crawlTm'] = item['modTM']['value'][0:22]
	zotItemUri = "https://www.zotero.org/groups/1892855/lexbib/items/"+itemdata[5]+"/item-details"
	target['details']['zotItemUri'] = zotItemUri
	target['details']['lexBibUri'] = "https://lexbib.elex.is/entity/"+itemuri
	if itemdata[7]:
		target['url'] = itemdata[7]
	else:
		print("Download/access URL missing.")
	collection = int(itemdata[2])
	target['details']['collection'] = collection
	#target['images']="https://raw.githubusercontent.com/elexis-eu/elexifinder/master/elexifinder/collection-images/collection_"+str(collection)+".jpg"
	target['images'] = [collection_images.images[collection]]
	print('Found image: '+target['images'][0])
#	if 'container' in item:
#		target['sourceUri'] = item['container']['value'] # replaced by containerFullTextUrl or containerUri
	# if 'containerFullTextUrl' in item:
	# 	target['sourceUri'] = item['containerFullTextUrl']['value']
	# 	target['url'] = item['containerFullTextUrl']['value'] # this overwrites zotero item in target['url']
	# elif 'containerUri' in item:
	if itemdata[8]:
		target['sourceUri'] = itemdata[8]
	else:
		print('Container URI missing.')
	# 	target['url'] = item['containerUri']['value'] # this overwrites zotero item in target['url']
	# if 'sourceUri' not in target:
	# 	print ('*** ERROR: nothing to use as sourceUri in '+itemuri+'!')
	# 	problemlog.append('*** ERROR: nothing to use as sourceUri in '+itemuri+'!\n')
	if itemdata[9]:
		target['sourceTitle'] = itemdata[9]
	else:
		print('Container Title missing.')

	target['lang'] = itemdata[6]
	if itemdata[11]:
		target['sourceLocUri'] = itemdata[11]
		target['sourceLocP'] = True
	else:
		target['sourceLocP'] = False
	if itemdata[12]:
		target['sourceCity'] = itemdata[12] # item['articleLocLabel']['value']
	if itemdata[13]:
		target['sourceCountry'] = itemdata[13] # item['articleCountryLabel']['value']
	if itemdata[10]:
		target['locationUri'] = itemdata[10]  # item['authorLoc']['value']
	if itemdata[7] != None: # this overwrites zotero item URL in target['url']
		target['url'] = itemdata[7] # item['fullTextUrl']['value']
	if itemdata[14] == "Q30":
		target['type'] = "video"
	else:
		target['type'] = "news" # item type for all except videos
	if itemuri in bodytxts:
		target['body'] = bodytxts[itemuri]['bodytxt']
		if len(target['body']) < 20: # at least an item title of 20 chars can serve as bodytxt
			add_missing_list(itemuri)
		print('Textbody found and copied.')
		if itemuri+".json" in wikidir:
			print('Found wikification result file for '+itemuri)
			with open(config.datafolder+'bodytxt/wikification/'+itemuri+'.json', 'r', encoding="utf-8") as jsonfile:
				wikiconcepts = json.load(jsonfile)
		else:
			print('Wikification still missing, will now be done for item '+itemuri)
			wikiconcepts = wikify.wikify(itemuri, target['body'])
		for wikiconcept in wikiconcepts['concepts']:
			wikiconcept['label'] = wikiconcept['label'].lower() # convert wikipage title to lowercase
			wikiconcept['uri'] = re.sub(r'^wd:Q', 'wikidata:Q', wikiconcept['uri']) # wikify.py returns "wd:" prefix for wikidata items
			if wikiconcept['label'].lower() not in labellist: # adds wikiconcept only if its label does not exist as lexvoc category label
				if wikiconcept['type'] == "person":
					print('Skipped wikiperson '+wikiconcept['label'])
				else:
					target['concepts'].append(wikiconcept)
		print('Wikiconcepts successfully added. Concept label list:')
		# for concept in target['concepts']:
		# 	print('* '+concept['label'])
	else:
		print('Textbody missing for this item.')
		add_missing_list(itemuri)


# upload to elexifinder
	print('Will upload BibItem '+itemuri+' to Elexifinder.')
	#print(str(target))
	addParams = {
	    "article": [json.dumps(target)],
	    "apiKey": EFapiKey
	}
	done = False
	attempts = 0
	while (not done):
		attempts += 1
		if attempts > 4:
			print('Elexifinder update failed 5 times. Abort.')
			with open(config.datafolder+'elexifinder/upload-errors.txt', 'a', encoding="utf-8") as errorfile:
				errorfile.write(itemuri+"\t"+str(datetime.now()).replace(' ','T')[0:22]+"\t"+str(errortext)+"\n")
			#sys.exit()
			break
		res = requests.post(EFhost + "/api/admin/v1/addArticle", json = addParams)
		print(res.json()['info'])
		if "Added 0 new articles" in res.json()['info']:
			errortext = res.json()['details'][0]['error']
			if "Article with the given URI" in errortext and "already exists" in errortext:
				removeParams = {
				    "articleUri": [itemuri],
				    "forceImmediateDelete": True,
				    "apiKey": EFapiKey
				}
				res = requests.post(EFhost + "/api/admin/v1/articleAdmin/deleteArticle", json = removeParams)
				print('Removed already existing article '+itemuri+'.')
				print(res.json()['info'])
			else:
				print('Elexifinder upload failed. Will try again. Error info was:')
				print(errortext)

				print(str(res.json()))
				time.sleep(1)
		else:
			done = True
	#print('Uploaded item '+itemuri+' to Elexifinder.')
	if done:
		donelist.append(itemuri)
		elexifinder.append(target)
		print('Finished item '+itemuri+'.')
		with open(config.datafolder+'elexifinder/export_last_donelist.txt', 'a', encoding="utf-8") as txt_file:
			txt_file.write(itemuri+'\n')
	else:
		print('Item could not be uploaded. Listed in upload_errors.txt')

# end of item loop



# with open(infile.replace('.json', '_problemlog.json'), 'w', encoding="utf-8") as problemfile:
# 	problemfile.write(str(problemlog))

elexidict = {}
for item in elexifinder:
	elexidict[item['uri']] = item

wikify.update_elexifinder_indices()


with open(config.datafolder+'elexifinder/export_last.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(elexidict, json_file, indent=2)
	print('\n=============================================\nCreated upload summary JSON file "export_last.json"... Finished.\n')
