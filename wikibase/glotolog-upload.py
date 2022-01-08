import json
import sys
import os
import time
import re
import langmapping
import lwb
import config

def gettitlelang():
	titlelang = None
	if 'inlgs' in bibdata[item]:
		if len(bibdata[item]['inlgs']) > 0:
			titlelangcand = bibdata[item]['inlgs'][0].replace("[","").replace("]","")
			print('title language candidate is: '+titlelangcand)
			titlelang = langmapping.getWikiLangCode(titlelangcand)
			if titlelang:
				print('Identified title language as: '+titlelang)
				return titlelang


# get donelist
with open(config.datafolder+'glottolog/glotolog-lwb-mapping.txt', 'r', encoding="utf-8") as txt_file:
	donelist = txt_file.read().split("\n")
	doneitems = {}
	for done in donelist:
		try:
			doneitems[done.split('|')[0]] = done.split('|')[1]
		except:
			pass

with open(config.datafolder+'glottolog/source_2_2_langqids.json', encoding="utf-8") as f:
	bibdata = json.load(f)

# jsonkeys = set()
# for url in bibdata:
# 	itemkeys = bibdata[url].keys()
# 	for key in itemkeys:
# 		jsonkeys.add(key)
#
# print(str(jsonkeys))
# with open(config.datafolder+'glottolog/glottolog_jsonkeys.json', 'w', encoding="utf-8") as jsonfile:
# 	json.dump(list(jsonkeys), jsonfile)
#
# sys.exit()
#

count = 0
for item in bibdata:
	count += 1
	print('\n['+str(count)+'] of ['+str(len(bibdata))+'] Now processing '+item)
	if item in doneitems.keys():
		# print('Item is in donelist, will skip: '+item)
		# continue
		qid = doneitems[item]
		print('Item is in donelist, qid is: '+qid)
		#continue
	else:
		qid = lwb.newitemwithlabel("Q4", 'en', bibdata[item]['title'])
		with open(config.datafolder+'glottolog/glotolog-lwb-mapping.txt', 'a', encoding="utf-8") as txt_file:
			txt_file.write(item+"|"+qid+"\n")

	glotostatement = lwb.updateclaim(qid,"P160",bibdata[item]['ID'],"string")

	if "doi" in bibdata[item]:
		lwb.updateclaim(qid,"P17",bibdata[item]['doi'],"string")

	if "oclc" in bibdata[item]:
		lwb.updateclaim(qid,"P62",bibdata[item]['oclc'],"string")

	if "metalanguages" in bibdata[item]:
		for lang in bibdata[item]['metalanguages']:
			lwb.updateclaim(qid,"P122",lang.replace("http://lexbib.elex.is/entity/",""),"item")

	if "objectlanguages" in bibdata[item]:
		for lang in bibdata[item]['objectlanguages']:
			lwb.updateclaim(qid,"P56",lang.replace("http://lexbib.elex.is/entity/",""),"item")

	if "entries" in bibdata[item]:
		lwb.updateclaim(qid,"P161",bibdata[item]['entries'],"string")

	if ("author" not in bibdata[item]) and ("editor" in bibdata[item]):
		bibdata[item]['author'] = bibdata[item]['editor']
	if "author" in bibdata[item]:
		authors = bibdata[item]['author'].split(" and ") # try to parse author lists separated with "and"
		for author in authors:
			authorlitstatement = lwb.updateclaim(qid,"P162",author,"string")

	distrostatement = lwb.updateclaim(qid,"P55",bibdata[item]['title'],"novalue")

	lwb.setref(distrostatement, "P108", item, "url")

	lwb.setqualifier(qid,"P55",distrostatement,"P91","Q14307","item")

	titlelang = gettitlelang()
	if "title_english" in bibdata[item]:
		lwb.setqualifier(qid,"P55",distrostatement,"P6",{'text':bibdata[item]['title_english'],'language':'en'},"monolingualtext")
		if titlelang != None and titlelang != "en":
			lwb.setqualifier(qid,"P55",distrostatement,"P6",{'text':bibdata[item]['title'],'language':titlelang},"monolingualtext")
			titlelang = "en_done"
	elif "title_german" in bibdata[item]:
		lwb.setqualifier(qid,"P55",distrostatement,"P6",{'text':bibdata[item]['title_german'],'language':'de'},"monolingualtext")
		if titlelang != None and titlelang != "de":
			lwb.setqualifier(qid,"P55",distrostatement,"P6",{'text':bibdata[item]['title'],'language':titlelang},"monolingualtext")
	if titlelang == None:
		titlelang = "en"
	if titlelang != "en_done":
		lwb.setqualifier(qid,"P55",distrostatement,"P6",{'text':bibdata[item]['title'],'language':titlelang},"monolingualtext")

	if "year" in bibdata[item]:
		try:
			assert len(bibdata[item]['year']) == 4
			intyear = int(bibdata[item]['year'])
			timestring = '+'+bibdata[item]['year']+'-01-01T00:00:00Z'
			print('Will try to write year as time object: '+timestring)
			lwb.setqualifier(qid,"P55",distrostatement,"P15",{'time':timestring,'precision':9},"time")
		except Exception as ex:
			print(str(ex))
			print('Time statement does not work. Will use publication year string instead, that does not fail...')
			lwb.setqualifier(qid,"P55",distrostatement,"P126",bibdata[item]['year'],"string")

	if "publisher" in bibdata[item]:
		publishers = bibdata[item]['publisher'].split("; ") # try to parse publisher lists separated with "; "
		for publisher in publishers:
			lwb.setqualifier(qid,"P55",distrostatement,"P163",publisher,"string")

	if "address" in bibdata[item]:
		addresses = bibdata[item]['address'].split("; ") # try to parse publishing place lists separated with "; "
		for address in addresses:
			lwb.setqualifier(qid,"P55",distrostatement,"P164",address,"string")

	if "isbn" in bibdata[item]:
		isbn = bibdata[item]['isbn'].replace("-","")
		if len(isbn) == 10:
			lwb.setqualifier(qid,"P55",distrostatement,"P19",isbn,"string")
		elif len(isbn) == 13:
			lwb.setqualifier(qid,"P55",distrostatement,"P18",isbn,"string")
		else:
			print("Error parsing ISBN literal: "+bibdata[item]['isbn'])

	print('Finished this item.\n')
	time.sleep(1)
