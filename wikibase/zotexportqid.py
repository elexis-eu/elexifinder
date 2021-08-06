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
#import urllib.parse
import eventmapping
import langmapping
import lwb
import config

# open and load input file
print('Please select Zotero export JSON to be processed.')
Tk().withdraw()
infile = askopenfilename()
print('This file will be processed: '+infile)
try:
	with open(infile, encoding="utf-8") as f:
		data =  json.load(f)
except Exception as ex:
	print ('Error: file does not exist.')
	print (str(ex))
	sys.exit()

# load list of already exported PDFs

with open('D:/LexBib/zot2wb/attachment_folders.csv', 'r', encoding="utf-8") as f:
	rows = csv.reader(f, delimiter = "\t")
	attachment_folder_list = {}
	for row in rows:
		attachment_folder_list[row[0]] = int(row[1])

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


	if re.match(r'^Q\d+', item['archive_location']):
		legacy_qid = re.match('^Q\d+',item['archive_location']).group(0)
		qid = lwb.getidfromlegid("Q3", legacy_qid)
		print('LexBib v2 legacy '+legacy_qid+' is v3 Qid: '+qid+'.')
		#return qid
	else:
		print('This item seems not to have any legacy (v2) Qid info at Zotero: '+item['id'])
		#return False
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

	# communicate with Zotero, write Qid to "archive location"
	zotapid = item['id'].replace("http://zotero.org/", "https://api.zotero.org/")

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
		json={"archiveLocation":"http://lexbib.elex.is/entity/"+qid,"version":version})

		if "204" in str(r):
			print('Successfully patched zotero item '+zotitemid+': '+qid)
			# with open(config.datafolder+'zoteroapi/lwbqid2zotero.csv', 'a', encoding="utf-8") as logfile:
			# 	logfile.write(qid+','+zotitemid+'\n')
			break
		print('Zotero API PATCH request failed ('+zotitemid+': '+qid+'), will repeat. Response was '+str(r)+str(r.content))
		time.sleep(2)

	if attempts > 4:
		print('Abort after 5 failed attempts.')
		sys.exit()

	return qid



# process Zotero export JSON

lwb_data = []
used_uri = []
seen_titles = []
seen_containers = []
itemcount = 0
for item in data:

	print("\nItem ["+str(itemcount+1)+"]: "+item['title'])
	if 'language' not in item:
		print('This item has no language, fatal error: '+item['id'])
	else:
		itemlang = langmapping.getiso3(item['language'])
		labellang = langmapping.getWikiLangCode(itemlang)
	if 'title' not in item:
		item['title'] = {"string":"","labellang":"und"}
	else:
		item['title'] = {"string":item['title'], "labellang":labellang}

	zotitemid = item['id'].replace("http://zotero.org/groups/1892855/items/", "")
	lexbibClass = ""
	# lexbibUri = define_uri(item)
	# if lexbibUri in used_uri:
	# 	print('***Fatal Error, attempt to use the same URI twice: '+lexbibUri)
	# 	sys.exit
	#
	# if not lexbibUri:
	# 	print('***Fatal Error, failed to define URI for item No. ['+str(itemcount+1)+']')
	# 	time.sleep(5)
	# else:
	# 	used_uri.append(lexbibUri)



	# iterate through zotero properties
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
					container = tag["tag"].replace(":container ","")
					if re.match(r'^Q\d+', container):
						contqid = container
					else:
						if container.startswith('isbn:') or container.startswith('oclc:'):
							container = container.replace("-","")
							container = container.replace("isbn:","http://worldcat.org/isbn/")
							container = container.replace("oclc:","http://worldcat.org/oclc/")
						elif container.startswith('doi:'):
							container = container.replace("doi:", "http://doi.org/")
						# check container type
						if item['type'] == "article-journal":
							contqid = lwb.getqid("Q1907", container) # Serials Publication volume Q1907. These are not member of Q3 (have no ZotItems)
						else:
							contqid = lwb.getqid("Q3", container)
						#lwb.itemclaim(contqid,"P5","Q12") # BibCollection Q12
						if contqid not in seen_containers:
							lwb.updateclaim(contqid,"P5","Q12","item") # BibCollection Q12
							seen_containers.append(contqid)
					propvals.append({"property":"P9","datatype":"item","value":contqid}) # container relation

					## get container short title from contained item and write to container
					# if item['type'] != "chapter" and "title-short" in item and item['title-short'] not in seen_titles:
					# 	lwb.updateclaim(qid, "P97", item['title-short'], "string")

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

		# Publication language. If language item does not exist, it is created. lexBibUri = lexvo uri
		elif zp == "language":
			propvals.append({"property":"P11","datatype":"item","value":itemlang})

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
			val = re.search(r'items/(.*)', val).group(1)
			propvals.append({"property":"P16","datatype":"string","value":val})
		elif zp == "title":
			propvals.append({"property":"P6","datatype":"string","value":val})
		elif zp == "container-title":
			propvals.append({"property":"P8","datatype":"string","value":val})
		elif zp == "event":
			propvals.append({"property":"P37","datatype":"string","value":val})
		elif zp == "page":
			propvals.append({"property":"P24","datatype":"string","value":val})
		elif zp == "publisher":
			propvals.append({"property":"P34","datatype":"novalue","value":"novalue","Qualifiers": [
			{"property":"P38","datatype":"string","value":val}]})
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
		elif zp == "journalAbbreviation":
			propvals.append({"property":"P54","datatype":"string","value":val})
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
					creatorvals.append({
					"property": prop,
					# "datatype": "string",
					# "value": creator["given"]+" "+creator["family"],
					"datatype": "novalue",
					"value": "novalue",
					"Qualifiers": [
					{"property":"P33","datatype":"string","value":str(listpos)},
					{"property": "P38","datatype":"string","value":creator["given"]+" "+creator["family"]},
					{"property":"P40","datatype":"string","value":creator["given"]},
					{"property":"P41","datatype":"string","value":creator["family"]}
					]
					})
					listpos += 1

		# Attachments
		elif zp == "attachments":
			txtfolder = None
			pdffolder = None
			for attachment in val:
				if not pdffolder and attachment['contentType'] == "application/pdf": # takes only the first PDF
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
					propvals.append({"property":"P70","datatype":"string","value":pdffolder})
				elif not txtfolder and attachment['contentType'] == "text/plain" and attachment['title'] != "pdf2text":
					txtloc = re.search(r'(D:\\Zotero\\storage)\\([A-Z0-9]+)\\(.*)', attachment['localPath'])
					txtfolder = txtloc.group(2)
					propvals.append({"property":"P71","datatype":"string","value":txtfolder})

		# Extra field, can contain a wikipedia page title, used in Elexifinder project as first-author-location-URI
		elif zp == "extra":
			place = val.replace("\n","").replace(" ","").split(";")[0].replace("http://","https://")
			if "en.wikipedia" in place:
				# check if this location is already in LWB, if it doesn't exist, create it
				if place in wpplaces:
					propvals.append({"property":"P29","datatype":"item","value":wpplaces[place]})
				else:
					print('This is an unkown place: '+place)
					sys.exit()
					# qid = lwb.getqid("Q9", place)
					# propvals.append({"property":"P29","datatype":"item","value":qid})

	lwb_data.append({"lexBibID":lexBibUri,"lexbibLegacyID":legacy_qid,"creatorvals":creatorvals,"propvals":propvals})
	itemcount += 1

# save updated attachment folder list
with open('D:/LexBib/zot2wb/attachment_folders.csv', 'w', encoding="utf-8") as attachment_folder_listfile:
	for item in attachment_folder_list:
		attachment_folder_listfile.write(item+"\t"+str(attachment_folder_list[item])+"\n")

#print(str(json.dumps(lwb_data)))
with open(infile.replace('.json', '_lwb_import_data.json'), 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(lwb_data, json_file, indent=2)
	print("\n=============================================\nCreated processed JSON file "+infile.replace('.json', '_lwb_import_data.json')+". Finished.")
	print("Now you probably will run bibimport, update places, grobidupload")
