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
import eventmapping
import langmapping
import lwb
import config

# ask for file to process
print('Please select Zotero export JSON to be processed.')
Tk().withdraw()
infile = askopenfilename()
print('This file will be processed: '+infile)

#load done items from previous runs
done_items = []
outfilename = infile.replace('.json', '_lwb_import_data.jsonl')
if os.path.exists(outfilename):
	with open(outfilename, encoding="utf-8") as outfile:
		doneits = outfile.read().split('\n')
		count = 0
		for doneit in doneits:
			count += 1
			if doneit != "":
				try:
					doneitjson = json.loads(doneit)
					#print(doneit)
					done_items.append(doneitjson['lexBibID'])
				except Exception as ex:
					print('Found unparsable doneit json in '+outfilename+' line ['+str(count)+']: '+doneit)
					print(str(ex))
					pass
#load input file
try:
	with open(infile, encoding="utf-8") as f:
		data =  json.load(f)
except Exception as ex:
	print ('Error: file does not exist.')
	print (str(ex))
	sys.exit()

# load list of place-mappings


wikipairs = {}
with open(config.datafolder+'mappings/wppage-wdid-mappings.json', encoding="utf-8") as f:
	wikipairs_orig =  json.load(f, encoding="utf-8")
	for placename in wikipairs_orig:
		wikipairs[urllib.parse.unquote(placename)] = wikipairs_orig[placename]
print('Wikiplace-pairs loaded.')


# load list of already exported PDFs

with open('D:/LexBib/zot2wb/attachment_folders.csv', 'r', encoding="utf-8") as f:
	rows = csv.reader(f, delimiter = "\t")
	attachment_folder_list = {}
	for row in rows:
		attachment_folder_list[row[0]] = int(row[1])

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

wpplaces = lwb.load_wppageplaces()

# # load list of already patched zotero items
# with open(config.datafolder+'zoteroapi/lwbqid2zotero.csv', 'r', encoding="utf-8") as logfile:
# 	donelog = csv.DictReader(logfile)
# 	doneqids = {}
# 	for row in donelog:
# 		doneqids[row['zotid']] = row['lwbqid']
# 	print('Loaded '+str(len(doneqids))+' done items.')


# define LexBib BibItem URI

def define_uri(item):
	# get LWB v2 legacy Qid, if any
	global linked_done
	global legacy_qid
	if re.match(r'^Q\d+', item['archive_location']):
		legacy_qid = re.match('^Q\d+',item['archive_location']).group(0)
		bibItemQid = lwb.getidfromlegid("Q3", legacy_qid)
	elif re.match(r'http://lexbib.elex.is/entity/(Q\d+)', item['archive_location']):
		bibItemQid = re.match(r'http://lexbib.elex.is/entity/(Q\d+)', item['archive_location']).group(1)
		legacy_qid = None
	else:
		print('*** Error: v2 '+legacy_qid+' has no v3 pendant. Will create new.')
		# with open(config.datafolder+"mappings/v2qid_no_v2qid.txt", "a", encoding="utf-8") as noqidlist:
		# 	noqidlist.write(bibItemQid+'\n')
		# 	return False
		bibItemQid = lwb.newitemwithlabel("Q3", "en", item['title']['text'])
		legacy_qid = None

	# set up new item

	# # check if this zotId exists on LWB
	# url = "https://data.lexbib.org/query/sparql?format=json&query=PREFIX%20ldp%3A%20%3Chttp%3A%2F%2Fdata.lexbib.org%2Fprop%2Fdirect%2F%3E%0Aselect%20%3Fqid%20where%0A%7B%3Fqid%20ldp%3AP16%20%3Chttp%3A%2F%2Flexbib.org%2Fzotero%2F"+zotitemid+"%3E.%20%7D"
	# done = False
	# while (not done):
	# 	try:
	# 		r = requests.get(url)
	# 		result = r.json()['results']['bindings']
	# 	except Exception as ex:
	# 		print('Error: SPARQL request failed: '+str(ex))
	# 		time.sleep(2)
	# 		continue
	# 	done = True
	# if len(result) > 0:
	# 	qid = result[0]['qid']['value'].replace("http://data.lexbib.org/entity/","")
	# 	print('Zotero ID '+zotitemid+' had been exported to '+qid+'; that mapping has disappeared from "archive location", will fix that...')
	#
	# 	lwb.logging.warning('Item mapping has disappeared from zotero data: ',zotitemid,qid)
	# else:
	# 	print('No Qid found for '+zotitemid+', neither in zotexport nor in LWB.')
	# 	qid = lwb.newitemwithlabel("Q3", "en", item['title'])

	# communicate with Zotero, write Qid to "archive location" and link to attachment (if not done before)

	zotapid = item['id'].replace("http://zotero.org/", "https://api.zotero.org/")
	zotitemid = re.search(r'items/(.*)',item['id']).group(1)
	# if zotitemid != leg_zotitemid:
	# 	print('\n*** ERROR: zotitemid v2 and v3 do not match for v3 '+bibItemQid+' and v2 '+legacy_qid+'!\n')
	if bibItemQid and bibItemQid not in linked_done:
		print('This item needs updated archive_loc and link attachment on Zotero.')
		attempts = 0
		while attempts < 5:
			attempts += 1
			r = requests.get(zotapid)
			if "200" in str(r):
				zotitem = r.json()
				print(zotitemid+': got zotitem data')
				break
			if "400" or "404" in str(r):
				print('*** Fatal error: Item '+zotitemid+' got '+str(r)+', does not exist on Zotero. Will skip.')
				time.sleep(5)
				break
			print('Zotero API GET request failed ('+zotitemid+'), will repeat. Response was '+str(r))
			time.sleep(2)

		if attempts < 5:
			version = zotitem['version']
		else:
			print('Abort after 5 failed attempts to get data from Zotero API.')
			sys.exit()

		#write to zotero

		attempts = 0
		while attempts < 5:
			attempts += 1
			r = requests.patch(zotapid,
			headers={"Zotero-API-key":config.zotero_api_key},
			json={"archiveLocation":"http://lexbib.elex.is/entity/"+bibItemQid,"version":version})

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



	return bibItemQid



# process Zotero export JSON

lwb_data = []
used_uri = []
seen_titles = []
new_places = []
seen_containers = []
legacy_qid = None
itemcount = 0
for item in data:
	print("\nItem ["+str(itemcount+1)+"]: "+item['title'])
	# get language codes and assign to item, title
	if 'language' not in item:
		print('This item has no language, fatal error: '+item['id'])
		item['language'] = "en"
	else:
		if item['language'] == "nor":
			item['language'] = "nbo" # "Norwegian (mixed) to Norwegian (Bokmal)"
	itemlangiso3 = langmapping.getiso3(item['language'])
	labellang = langmapping.getWikiLangCode(itemlangiso3)
	itemlangqid = langmapping.getqidfromiso(itemlangiso3)
	if 'title' in item:
		item['title'] = {"text":item['title'], "language":labellang}
	# else:
	# 	item['title'] =
	lexbibClass = ""
	bibItemQid = define_uri(item)

	if bibItemQid in done_items:
		itemcount += 1
		continue

	if bibItemQid in used_uri:
		print('***Fatal Error, attempt to use the same URI twice: '+bibItemQid)
		sys.exit()

	if bibItemQid == False:
		print('***Fatal Error, failed to define URI for item No. ['+str(itemcount+1)+']')
		sys.exit()
	else:
		used_uri.append(bibItemQid)


	# get lexbib v2 legacy item data
	if legacy_qid:
		query = """
		PREFIX lwb: <http://data.lexbib.org/entity/>
		PREFIX ldp: <http://data.lexbib.org/prop/direct/>
		PREFIX lp: <http://data.lexbib.org/prop/>
		PREFIX lps: <http://data.lexbib.org/prop/statement/>
		PREFIX lpq: <http://data.lexbib.org/prop/qualifier/>
		PREFIX lpr: <http://data.lexbib.org/prop/reference/>
		PREFIX owl: <http://www.w3.org/2002/07/owl#>

		select ?bibItem
		(group_concat(distinct concat('"',str(?aulistpos),'":"',strafter(str(?author),"http://data.lexbib.org/entity/"),'"');SEPARATOR=", ") as ?leg_authors)
		(group_concat(distinct concat('"',str(?edlistpos),'":"',strafter(str(?editor),"http://data.lexbib.org/entity/"),'"');SEPARATOR=", ") as ?leg_editors)
		(strafter(str(?container),"http://data.lexbib.org/entity/") as ?leg_container)
		(strafter(str(?zotero),"http://lexbib.org/zotero/") as ?zotid)
		where {
		  BIND(lwb:"""+legacy_qid+""" as ?bibItem)
		  ?bibItem ldp:P5 lwb:Q3.
		  OPTIONAL{ ?bibItem lp:P12 ?authorstatement.
				   ?authorstatement lps:P12 ?author.
		  ?authorstatement lpq:P33 ?aulistpos .}
		   OPTIONAL {?bibItem lp:P13 ?editorstatement.
		  ?editorstatement lps:P13 ?editor.
		  ?editorstatement lpq:P33 ?edlistpos .}
		   OPTIONAL {?bibItem  ldp:P9 ?container. }
			  ?bibItem	 ldp:P16 ?zotero.


		} group by ?bibItem ?leg_authors ?leg_editors ?container ?zotero"""

		v2url = "https://data.lexbib.org/query/sparql"
		print("Waiting for LexBib v2 SPARQL ("+legacy_qid+")...")
		sparqlresults = sparql.query(v2url,query)
		print('Got data for this item from LexBib v2 SPARQL.')

		#go through sparqlresults
		done = False
		while not done:
			leg_zotitemid = None
			for row in sparqlresults:
				sparqlitem = sparql.unpack_row(row, convert=None, convert_type={})
				#print('\nv2 bibItem content is '+str(sparqlitem))
				leg_authors = {}
				if sparqlitem[1]:
					aujson = json.loads("{"+sparqlitem[1]+"}")
					#print(str(aujson))
					for lp in range(len(aujson)):
						leg_authors[lp+1] = aujson[str(lp+1)]
					#print(str(leg_authors))
				leg_editors = {}
				if sparqlitem[2]:
					edjson = json.loads("{"+sparqlitem[2]+"}")
					for lp in range(len(edjson)):
						leg_editors[lp+1] = edjson[str(lp+1)]
				leg_container = None
				if sparqlitem[3]:
					leg_container = sparqlitem[3]
				leg_zotitemid = sparqlitem[4]
				done = True
			if not done:
				print('SPARQL returned no result for v2 ID '+legacy_qid)
				time.sleep(2)

		print('SPARQL data successfully parsed.')
	else:
		leg_authors = {}
		leg_editors = {}


	# iterate through zotero properties and write RDF triples
	creatorvals = []
	propvals = []

	for zp in item: # zp: zotero property
		val = item[zp] # val: value of zotero property


		# lexbib zotero tags can contain statements (shortcode for property, and value).
		# If item as value, and that item does not exist, it is created.
		if zp == "tags":
			for tag in val:
				if tag["tag"].startswith(':event '):
					eventcode = tag["tag"].replace(":event ","")
					if eventcode not in eventmapping.mapping:
						print('***ERROR: event not existing in lwb: '+eventcode)
						sys.exit()
					eventqid = eventmapping.mapping[eventcode]
					propvals.append({"property":"P36","datatype":"item","value":eventqid})
				if tag["tag"].startswith(':container '):
					# container = tag["tag"].replace(":container ","")
					# if re.match(r'^Q\d+', container):
					# 	contqid = container
					# else:
					# 	if container.startswith('isbn:') or container.startswith('oclc:'):
					# 		container = container.replace("-","")
					# 		container = container.replace("isbn:","http://worldcat.org/isbn/")
					# 		container = container.replace("oclc:","http://worldcat.org/oclc/")
					# 	elif container.startswith('doi:'):
					# 		container = container.replace("doi:", "http://doi.org/")
					# 	# check container type
					# 	if item['type'] == "article-journal":
					# 		contqid = lwb.getqid("Q1907", container) # Serials Publication volume Q1907. These are not member of Q3 (=have no ZotItems)
					# 	else:
					# 		contqid = lwb.getqid("Q3", container)
					# 	#lwb.itemclaim(contqid,"P5","Q12") # BibCollection Q12
					# 	if contqid not in seen_containers:
					# 		lwb.updateclaim(contqid,"P5","Q12","item") # BibCollection Q12
					# 		seen_containers.append(contqid)
					if leg_container:
						v3container = lwb.legacyID[leg_container]
						propvals.append({"property":"P9","datatype":"item","value":v3container}) # container relation


					# get container short title from contained item and write to container
					if item['type'] != "chapter" and "title-short" in item and item['title-short'] not in seen_titles:
						lwb.updateclaim(v3container, "P97", item['title-short'], "string")
						seen_titles.append(item['title-short'])

				if tag["tag"].startswith(':type '):
					type = tag["tag"].replace(":type ","")
					if type == "Review":
						propvals.append({"property":"P5","datatype":"item","value":"Q15"})
					elif type == "Report":
						propvals.append({"property":"P5","datatype":"item","value":"Q25"})
					elif type == "Proceedings":
						propvals.append({"property":"P5","datatype":"item","value":"Q18"})
					elif type == "Dictionary":
						propvals.append({"property":"P5","datatype":"item","value":"Q24"}) # LCR distribution
					elif type == "Software":
						lexbibClass = "Q13" # this will override item type "book"
						#propvals.append({"property":"P5","datatype":"item","value":"Q13"})
					elif type == "Community":
						propvals.append({"property":"P5","datatype":"item","value":"Q26"})

				if tag["tag"].startswith(':collection '):
					coll = tag["tag"].replace(":collection ","")
					propvals.append({"property":"P85","datatype":"string","value":coll})

		# Publication language
		elif zp == "language":
			propvals.append({"property":"P11","datatype":"item","value":itemlangqid})

		### bibitem type mapping
		elif zp == "type" and lexbibClass == "": # setting lexbibClass before overrides this bibItem type P100 setting

			if val == "paper-conference":
				propvals.append({"property":"P100","datatype":"item","value":"Q27"})
			elif val == "article-journal":
				propvals.append({"property":"P100","datatype":"item","value":"Q19"})
			elif val == "book":
				propvals.append({"property":"P100","datatype":"item","value":"Q28"})
			elif val == "chapter":
				propvals.append({"property":"P100","datatype":"item","value":"Q29"})
			elif val == "motion_picture": # videos
				propvals.append({"property":"P100","datatype":"item","value":"Q30"})
			elif val == "speech":
				propvals.append({"property":"P100","datatype":"item","value":"Q31"})
			elif val == "thesis":
				propvals.append({"property":"P100","datatype":"item","value":"Q32"})


		### props with literal value
		elif zp == "id":
			zotitemid = re.search(r'items/(.*)', val).group(1)
			propvals.append({"property":"P16","datatype":"string","value":zotitemid})
		elif zp == "title":
			propvals.append({"property":"P6","datatype":"monolingualtext","value":val})
		# elif zp == "container-title":
		#	propvals.append({"property":"P8","datatype":"string","value":val})
		# elif zp == "event":
		# 	propvals.append({"property":"P37","datatype":"string","value":val})
		elif zp == "page":
			propvals.append({"property":"P24","datatype":"string","value":val})
		elif zp == "publisher":
			vallist = val.split(";")
			for val in vallist:
				propvals.append({"property":"P35","datatype":"novalue","value":"novalue","Qualifiers": [
				{"property":"P38","datatype":"string","value":val.strip()}]})
		elif zp == "DOI":
			if "http://" in val or "https://" in val:
				val = re.search(r'/(10\..+)$', val).group(1)
			propvals.append({"property":"P17","datatype":"string","value":val})
		elif zp == "ISSN":
			if "-" not in val: # normalize ISSN, remove any secondary ISSN
				val = val[0:4]+"-"+val[4:9]
			propvals.append({"property":"P20","datatype":"string","value":val[:9]})
		elif zp == "ISBN":
			val = val.replace("-","")
			val = re.search(r'^\d+',val).group(0)
			if len(val) == 10:
				propvals.append({"property":"P19","datatype":"string","value":val})
			elif len(val) == 13:
				propvals.append({"property":"P18","datatype":"string","value":val})
		elif zp == "volume" and item['type'] == "article-journal": # volume only for journals (book series also have "volume")
			propvals.append({"property":"P22","datatype":"string","value":val})
		elif zp == "issue" and item['type'] == "article-journal": # issue only for journals
			propvals.append({"property":"P23","datatype":"string","value":val})
		# elif zp == "journalAbbreviation":
		# 	propvals.append({"property":"P54","datatype":"string","value":val})
		elif zp == "URL":
			propvals.append({"property":"P21","datatype":"string","value":val})
		elif zp == "issued":
			year = val["date-parts"][0][0]
			precision = 9
			#propvals.append({"property":"P14","datatype":"string","value":year})
			if len(val["date-parts"][0]) > 1:
				month = str(val["date-parts"][0][1])
				if len(month) == 1:
					month = "0"+month
				precision = 10
			else:
				month = "01"
			if len(val["date-parts"][0]) > 2:
				day = str(val["date-parts"][0][2])
				if len(day) == 1:
					day = "0"+day
				precision = 11
			else:
				day = "01"
			timestr = "+"+year+"-"+month+"-"+day+"T00:00:00Z"
			propvals.append({"property":"P15","datatype":"time","value":{"time":timestr,"precision":precision}})
		elif zp == "edition":
			propvals.append({"property":"P64","datatype":"string","value":val})
		elif zp == "author" or zp == "editor":
			if zp == "author":
				prop = "P12"
			elif zp == "editor":
				prop = "P13"
			listpos = 1
			for creator in val:
				if "literal" in creator: # this means there is no firstname-lastname but a single string (for Orgs):
					pass # TBD
				else:
					if "non-dropping-particle" in creator:
						creator["family"] = creator["non-dropping-particle"]+" "+creator["family"]
					if creator["family"] == "Various":
						creator["given"] = "Various"
					# get v2 legacy creator items
					if zp == "author":
						if listpos in leg_authors:
							creatordatatype = "item"
							creatorv3qid = lwb.getidfromlegid("Q5", leg_authors[listpos])
						else:
							creatordatatype = "novalue"
							creatorv3qid = "novalue"
					elif zp == "editor":
						if listpos in leg_editors:
							creatordatatype = "item"
							creatorv3qid = lwb.legacyID[leg_editors[listpos]]
						else:
							creatordatatype = "novalue"
							creatorv3qid = "novalue"

					creatorvals.append({
					"property": prop,
					# "datatype": "string",
					# "value": creator["given"]+" "+creator["family"],
					# "datatype": "novalue",
					# "value": "novalue",
					"datatype": creatordatatype,
					"value": creatorv3qid,
					"Qualifiers": [
					{"property":"P33","datatype":"string","value":str(listpos)},
					{"property":"P38","datatype":"string","value":creator["given"]+" "+creator["family"]},
					{"property":"P40","datatype":"string","value":creator["given"]},
					{"property":"P41","datatype":"string","value":creator["family"]}
					]
					})
					# for v3 definitive, this has to go one level to the left
					listpos += 1

		# Attachments
		elif zp == "attachments":
			txtfolder = None
			txttype = None
			pdffolder = None
			for attachment in val:
				if attachment['contentType'] == "application/pdf" and not pdffolder: # takes only the first PDF
					pdfloc = re.search(r'(D:\\Zotero\\storage)\\([A-Z0-9]+)\\(.*)', attachment['localPath'])
					pdfpath = pdfloc.group(1)
					pdffolder = pdfloc.group(2)
					pdfoldfile = pdfloc.group(3)
					pdfnewfile = pdffolder+".pdf" # rename file to <folder>.pdf
					if pdffolder not in attachment_folder_list or attachment_folder_list[pdffolder] < attachment['version']:
						copypath = 'D:\\LexBib\\zot2wb\\grobid_upload\\'+pdffolder
						if not os.path.isdir(copypath):
							os.makedirs(copypath)
						shutil.copy(pdfpath+'\\'+pdffolder+'\\'+pdfoldfile, copypath+'\\'+pdfnewfile)
						print('Found and copied to GROBID upload folder '+pdfnewfile)
						attachment_folder_list[pdffolder] = attachment['version']
						# save new PDF location to listfile
						with open('D:/LexBib/zot2wb/attachment_folders.csv', 'a', encoding="utf-8") as attachment_folder_listfile:
							attachment_folder_listfile.write(pdffolder+"\t"+str(attachment['version'])+"\n")
					propvals.append({"property":"P70","datatype":"string","value":pdffolder})
				elif attachment['contentType'] == "text/plain": # prefers cleantext or any other over grobidtext
					txtloc = re.search(r'(D:\\Zotero\\storage)\\([A-Z0-9]+)\\(.*)', attachment['localPath']).group(2)
					filetype = None
					if "GROBID" not in attachment['title'] and "pdf2txt" not in attachment['title'] and "pdf2text" not in attachment['title']:
						txtfolder = txtloc
						txttype = "clean"
					elif txttype != "clean" and "pdf2txt" not in attachment['title'] and "pdf2text" not in attachment['title']:
						txtfolder = txtloc
						txttype = "GROBID or other"
			if txtfolder:
				propvals.append({"property":"P71","datatype":"string","value":txtfolder})

		# Extra field, can contain a wikipedia page title, used in Elexifinder project as first-author-location-URI
		elif zp == "extra":
			wppage = urllib.parse.unquote(val.replace("\n","").replace(" ","").split(";")[0].replace("http://","https://"))

			if "en.wikipedia" in wppage:
				print('Found authorloc wppage: '+wppage)
				# check if this location is already in LWB, if it doesn't exist, create it
				wppagetitle = wppage.replace("https://en.wikipedia.org/wiki/","")
				if wppagetitle not in wikipairs:
					wdjsonsource = requests.get(url='https://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&format=json&titles='+wppage)
					wdjson =  wdjsonsource.json()
					entities = wdjson['entities']
					for wdid in entities:
						print("found new wdid on wikidata"+wdid+" for AUTHORLOC "+wppage)
						placeqid = lwb.wdid2lwbid(wdid)
				else:
					wdid = wikipairs[wppagetitle]
					placeqid = lwb.wdid2lwbid(wdid)
				if placeqid:
						print("This is a known authorloc: "+placeqid)
				else:
					print("This is an unknown place an will be created: "+wppagetitle)
					placeqid = lwb.newitemwithlabel("Q9", "en", wppagetitle)
					wdstatement = lwb.stringclaim(placeqid, "P2", wdid)
					wpstatement = lwb.stringclaim(placeqid, "P66", wppage)
					lwb.save_wdmapping({"lwbid": placeqid, "wdid": wdid})
					lwb.wdids[placeqid] = wdid
					new_places.append({"placeQid":placeqid,"wppage":wppage, "wdid":wdid})
				propvals.append({"property":"P29","datatype":"item","value":placeqid})


			else:
				print('Found NO authorloc wppage.')

	with open(outfilename, 'a', encoding="utf-8") as outfile:
		outfile.write(json.dumps({"lexBibID":bibItemQid,"lexbibLegacyID":legacy_qid,"creatorvals":creatorvals,"propvals":propvals})+'\n')
	print('Triples successfully defined.')
	itemcount += 1



#print(str(json.dumps(lwb_data)))
# with open(infile.replace('.json', '_lwb_import_data.json'), 'w', encoding="utf-8") as json_file: # path to result JSON file
#	json.dump(lwb_data, json_file, indent=2)
print("\n=============================================\nCreated processed JSON file "+infile.replace('.json', '_lwb_import_data.json')+". Finished.")
print("Now you probably will run bibimport, update placemapping, grobidupload\n")
print('New places:')
print(str(new_places))
with open('newplaces.json', 'a', encoding="utf-8") as placesfile:
	json.dump(new_places, placesfile, indent=2)

# save known wikipedia-wikidata mappings to file
with open(config.datafolder+'mappings/wppage-wdid-mappings.json', 'w', encoding="utf-8") as mappingfile:
	json.dump(wikipairs, mappingfile, ensure_ascii=False, indent=2)
print('\nsaved known Wikipedia-Wikdiata mappings.')
