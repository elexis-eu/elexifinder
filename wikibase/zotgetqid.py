from tkinter import Tk
from tkinter.filedialog import askopenfilename
import time
import sys
import json
import csv
import re
import unidecode
import os
import shutil
import requests
import sparql
import urllib.parse
import collections
# import eventmapping
import langmapping
import lwb
import config
from pyzotero import zotero
pyzot = zotero.Zotero(1892855,'group',config.zotero_api_key)

# load zotero-to-wikibase link-attachment mapping

linked_done = {}
with open(config.datafolder+'mappings/linkattachmentmappings.jsonl', encoding="utf-8") as jsonl_file:
	mappings = jsonl_file.read().split('\n')
	count = 0
	for mapping in mappings:
		count += 1
		if mapping != "":
			try:
				mappingjson = json.loads(mapping)
				#print(mapping)
				linked_done[mappingjson['bibitem']] = {"itemkey":mappingjson['itemkey'],"attkey":mappingjson['attkey']}
			except Exception as ex:
				print('Found unparsable mapping json in linkattachmentmappings.jsonl line ['+str(count)+']: '+mapping)
				print(str(ex))
				pass

#get tag "_getqid" lexbib zotero items
print('Will now get LexBib zotero items with tag "_getqid"...')
tagzotitems = pyzot.items(tag="_getqid")

# first loop: BibItem creation and Qid to Zotero
for item in tagzotitems:
	if re.match(r'http://lexbib.elex.is/entity/(Q\d+)', item['data']['archiveLocation']):
		bibItemQid = re.match(r'http://lexbib.elex.is/entity/(Q\d+)', item['data']['archiveLocation']).group(1)
		print('This item already has a LWB qid (field "archive location"): '+bibItemQid)
		continue
	if item['data']['archiveLocation'] != "":
		print('*** Field "archive location" is not empty. Skipped.')
		continue

	print('Creating a new Wikibase item...')
	bibItemQid = lwb.newitemwithlabel(["Q3"], "en", item['data']['title'])

	zotapid = item['links']['self']['href']
	zotitemid = item['key']


	#write to zotero AN field

	attempts = 0
	while attempts < 5:
		attempts += 1
		r = requests.patch(zotapid,
		headers={"Zotero-API-key":config.zotero_api_key},
		json={"archiveLocation":"http://lexbib.elex.is/entity/"+bibItemQid,"version":item['version']})

		if "204" in str(r):
			print('Successfully patched zotero item '+zotitemid+': '+bibItemQid)
			# with open(config.datafolder+'zoteroapi/lwbqid2zotero.csv', 'a', encoding="utf-8") as logfile:
			# 	logfile.write(qid+','+zotitemid+'\n')
			break
		print('Zotero API PATCH request failed ('+zotitemid+': '+bibItemQid+'), will repeat. Response was '+str(r)+str(r.content))
		time.sleep(2)

	if attempts > 4:
		print('Abort after 5 failed attempts.')
		sys.exit()


	# attach link to wikibase
	attachment = [
	{
	"itemType": "attachment",
	"parentItem": zotitemid,
	"linkMode": "linked_url",
	"title": "LexBib Linked Data",
	"accessDate": "2021-08-08T00:00:00Z",
	"url": "http://lexbib.elex.is/entity/"+bibItemQid,
	"note": '<p>See this item as linked data at <a href="http://lexbib.elex.is/entity/'+bibItemQid+'">http://lexbib.elex.is/entity/'+bibItemQid+'</a>',
	"tags": [],
	"collections": [],
	"relations": {},
	"contentType": "",
	"charset": ""
	}
	]

	r = requests.post('https://api.zotero.org/groups/1892855/items', headers={"Zotero-API-key":config.zotero_api_key, "Content-Type":"application/json"} , json=attachment)

	if "200" in str(r):
		#print(r.json())
		attkey = r.json()['successful']['0']['key']
		linked_done[bibItemQid] = {"itemkey":zotitemid,"attkey":attkey}
		with open(config.datafolder+'mappings/linkattachmentmappings.jsonl', 'a', encoding="utf-8") as jsonl_file:
			jsonline = {"bibitem":bibItemQid,"itemkey":zotitemid,"attkey":attkey}
			jsonl_file.write(json.dumps(jsonline)+'\n')
		print('Zotero item link attachment successfully written and bibitem-attkey mapping stored; attachment key is '+attkey+'.')
	else:
		print('Failed writing link attachment to Zotero item '+zotitemid+'.')

print('\nFinished first loop: BibItem creation and linking.\n')

# second loop: check container relations
seen_containers = {}
tagzotitems = pyzot.items(tag="_getqid") # get data again (with new version numbers)
for item in tagzotitems:
	for tag in item['data']['tags']:
		if tag["tag"].startswith(':container '):
			container = tag["tag"].replace(":container ","")

			if re.match(r'^Q\d+', container): # LexBib version 3 container item is already created and linked
				print('Found known v3 container already created and linked.')

			elif re.match(r'^https?://', container): # old LexBib v2 container tag (landing page url)
													 # or newly added container-link
													 # (i.e. journal issue landing page URL as value for ":container") found,
													 # will be updated to v3 container tag
				containername = re.sub(r'^https?://','',container)
				print('Found http-container: '+containername)
				if containername in seen_containers:
					v3container = seen_containers[containername]
					print('Container already created in this same run: '+str(v3container))
				else:
					print('Will check if this exists already on LWB; waiting for SPARQL...')
					# check if container already exists (TBD)
					query ="""
							PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
							select ?item ?itemLabel where
							{?item ldp:P44|ldp:P111 <"""+container+"""> ; rdfs:label ?itemLabel . filter(lang(?itemLabel)="en")
							 }"""
					sparqlresults = sparql.query('https://lexbib.elex.is/query/sparql',query)
					print('Got data from LexBib v3 SPARQL.')
					#go through sparqlresults
					v3container = None
					for row in sparqlresults:
						sparqlitem = sparql.unpack_row(row, convert=None, convert_type={})
						print(str(sparqlitem))
						if sparqlitem[0].startswith("http://lexbib.elex.is/entity/Q"):
							v3container = sparqlitem[0].replace("http://lexbib.elex.is/entity/","")
							print('This container has been found by SPARQL, will rename tag to '+v3container)
					if not v3container: # no container item found
						# create new container item

						print('Nothing found. Will create new container item.')
						# TBD: other bibitem types
						if item['data']['itemType'] == "journalArticle":
							if "ISSN" in item['data']:
								if "-" not in item['data']['ISSN']: # normalize ISSN, remove any secondary ISSN
									contissn = item['data']['ISSN'][0:4]+"-"+item['data']['ISSN'][4:9]
								else:
									contissn = item['data']['ISSN'][:9]
							else:
								contissn = None

							contlabel = ""
							if item['data']["publicationTitle"] != "":
								contlabel += item['data']['publicationTitle']
							voliss = ""
							if item['data']["volume"] != "":
								voliss += item['data']['volume']
							if item['data']["volume"] != "" and item['data']["issue"] != "":
								voliss += "/"
							if item['data']["issue"] != "":
								voliss += item['data']['issue']
							if voliss != "":
								voliss = " "+voliss
							contyear = " ("+item['meta']['parsedDate'][0:4]+")"

							v3container = lwb.newitemwithlabel("Q12","en",contlabel+voliss+contyear)
							print('New container item is: '+str(v3container)+" "+contlabel+voliss+contyear)
							print('Will write container entity data.')
							lwb.itemclaim(v3container,"P5","Q16")
							if contissn:
								lwb.stringclaim(v3container,"P20",contissn)
							if "volume" in item['data']:
								lwb.stringclaim(v3container,"P22",item['data']['volume'])
							if "issue" in item['data']:
								lwb.stringclaim(v3container,"P23",item['data']['issue'])
							lwb.stringclaim(v3container,"P111",container)
							lwb.stringclaim(v3container,"P97",contlabel+voliss+contyear)

					# update zotero container tags for all items that point to this container
					print('Will now update zotero tags to v3 container tag...')
					tagzotitems = pyzot.items(tag=":container "+container)
					for tagzotitem in tagzotitems:
						pyzot.add_tags(tagzotitem, ":container "+v3container)
						print('container-tag '+v3container+' written to '+tagzotitem['key'])
						time.sleep(0.2)
					pyzot.delete_tags(":container "+container)
					print('Zotero container tag '+container+' updated to '+v3container)
					seen_containers[containername] = v3container

print('Finished second loop: Container relation.\n')

pyzot.delete_tags("_getqid")
print('Zotero tag "_getqid" removed from '+str(len(tagzotitems))+' items.\nFinished.')
