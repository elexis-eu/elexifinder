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
import langmapping
import lwb
import config

# ask for file to process

infile = config.datafolder+'quickexport2.json'
print('This file will be processed: '+infile)

#load done items from previous runs
done_items = []
outfilename = infile.replace('.json', '_donelist.jsonl')
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
	print('Donelist loaded.')
else:
	print('No donelist loaded.')
#load input file
try:
	with open(infile, encoding="utf-8") as f:
		data =  json.load(f)
except Exception as ex:
	print ('Error: file does not exist.')
	print (str(ex))
	sys.exit()

# # load list of place-mappings
#
#
# wikipairs = {}
# with open(config.datafolder+'mappings/wppage-wdid-mappings.json', encoding="utf-8") as f:
# 	wikipairs_orig =  json.load(f, encoding="utf-8")
# 	for placename in wikipairs_orig:
# 		wikipairs[urllib.parse.unquote(placename)] = wikipairs_orig[placename]
# print('Wikiplace-pairs loaded.')


# # load list of already exported PDFs
#
# with open('D:/LexBib/zot2wb/attachment_folders.csv', 'r', encoding="utf-8") as f:
# 	rows = csv.reader(f, delimiter = "\t")
# 	attachment_folder_list = {}
# 	for row in rows:
# 		attachment_folder_list[row[0]] = int(row[1])

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

# define LexBib BibItem URI

def define_uri(item):
	# get LWB v2 legacy Qid, if any
	global zotitemid
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

	# communicate with Zotero, write Qid to "archive location" and link to attachment (if not done before)

	zotapid = item['id'].replace("http://zotero.org/", "https://api.zotero.org/")

	if bibItemQid and bibItemQid not in linked_done:
		print('This item needs updated archive_loc and link attachment on Zotero.')
		attempts = 0
		while attempts < 5:
			attempts += 1
			try:
				r = requests.get(zotapid)
				if "200" in str(r):
					zotitem = r.json()
					print(zotitemid+': got zotitem data')
					break
				if "400" or "404" in str(r):
					print('*** Fatal error: Item '+zotitemid+' got '+str(r)+', does not exist on Zotero. Will skip.')
					time.sleep(5)
					break
			except Exception as ex:
				print('Zotero API GET request failed ('+zotitemid+'), will wait 15 sec. and repeat.\nResponse was: '+str(r)+'\nError was: '+str(ex))
				time.sleep(15)

		if attempts < 5:
			version = zotitem['version']
		else:
			print('Abort after 5 failed attempts to get data from Zotero API.')
			sys.exit()

		#write to zotero

		attempts = 0
		while attempts < 5:
			attempts += 1
			try:
				r = requests.patch(zotapid,
				headers={"Zotero-API-key":config.zotero_api_key},
				json={"archiveLocation":"http://lexbib.elex.is/entity/"+bibItemQid,"version":version})

				if "204" in str(r):
					print('Successfully patched zotero item '+zotitemid+': '+bibItemQid)
					# with open(config.datafolder+'zoteroapi/lwbqid2zotero.csv', 'a', encoding="utf-8") as logfile:
					# 	logfile.write(qid+','+zotitemid+'\n')
					break
			except Exception as ex:
				print('Zotero API PATCH request failed ('+zotitemid+': '+bibItemQid+'), will repeat. Response was '+str(r)+str(r.content))
				time.sleep(10)

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
		try:
			r = requests.post('https://api.zotero.org/groups/1892855/items', headers={"Zotero-API-key":config.zotero_api_key, "Content-Type":"application/json"} , json=attachment)

			if "200" in str(r):
				#print(r.json())
				attkey = r.json()['successful']['0']['key']
				linked_done[bibItemQid] = {"itemkey":zotitemid,"attkey":attkey}
				with open(config.datafolder+'mappings/linkattachmentmappings.jsonl', 'a', encoding="utf-8") as jsonl_file:
					jsonline = {"bibitem":bibItemQid,"itemkey":zotitemid,"attkey":attkey}
					jsonl_file.write(json.dumps(jsonline)+'\n')
				print('Zotero item link attachment successfully written and bibitem-attkey mapping stored; attachment key is '+attkey+'.')
		except:
			print('Failed writing link attachment to Zotero item '+zotitemid+'.')
	else:
		print('This Zotero item has already been linked to lexbib.elex.is.')




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
	# if 'title' in item:
	# 	item['title'] = {"text":item['title'], "language":labellang}
	# else:
	# 	item['title'] = ""
	#
	zotitemid = re.search(r'items/(.*)',item['id']).group(1)
	bibItemQid = define_uri(item)

	if bibItemQid in done_items:
		itemcount += 1
		print('This item has been finished in a previous run.')
		continue

	if bibItemQid in used_uri:
		print('***Fatal Error, attempt to use the same URI twice: '+bibItemQid)
		sys.exit()

	if bibItemQid == False:
		print('***Fatal Error, failed to define URI for item No. ['+str(itemcount+1)+']')
		sys.exit()
	else:
		used_uri.append(bibItemQid)

	langstatement = lwb.updateclaim(bibItemQid, "P11", itemlangqid, "item")

	# zotitemstatement = lwb.updateclaim(bibItemQid, "P16", zotitemid, "string")
	#
	# abslangqid = None
	# if "tags" in item:
	# 	for tag in item['tags']:
	# 		if tag["tag"].startswith(':abstractLanguage '):
	# 			abslangcode = tag["tag"].replace(":abstractLanguage ","")
	# 			abslangiso3 = langmapping.getiso3(abslangcode)
	# 			abslangqid = langmapping.getqidfromiso(abslangiso3)
	# 		if tag["tag"].startswith(':collection '):
	# 			coll = tag["tag"].replace(":collection ","")
	# 			lwb.updateclaim(bibItemQid, "P85", coll, "string")
	#
	# if "abstract" in item:
	# 	if len(item['abstract']) > 20:
	# 		if not abslangqid:
	# 			abslangqid = itemlangqid
	# 		lwb.setqualifier(bibItemQid,"P16",zotitemstatement,"P105",abslangqid,"item")
	# # Attachments
	# if "attachments" in item:
	# 	txtfolder = None
	# 	txttype = None
	# 	pdffolder = None
	# 	for attachment in item['attachments']:
	# 		if attachment['contentType'] == "application/pdf" and not pdffolder: # takes only the first PDF
	# 			pdfloc = re.search(r'(D:\\Zotero\\storage)\\([A-Z0-9]+)\\(.*)', attachment['localPath'])
	# 			pdfpath = pdfloc.group(1)
	# 			pdffolder = pdfloc.group(2)
	# 			# pdfoldfile = pdfloc.group(3)
	# 			# pdfnewfile = pdffolder+".pdf" # rename file to <folder>.pdf
	# 			# if pdffolder not in attachment_folder_list or attachment_folder_list[pdffolder] < attachment['version']:
	# 			# 	copypath = 'D:\\LexBib\\zot2wb\\grobid_upload\\'+pdffolder
	# 			# 	if not os.path.isdir(copypath):
	# 			# 		os.makedirs(copypath)
	# 			# 	shutil.copy(pdfpath+'\\'+pdffolder+'\\'+pdfoldfile, copypath+'\\'+pdfnewfile)
	# 			# 	print('Found and copied to GROBID upload folder '+pdfnewfile)
	# 			# 	attachment_folder_list[pdffolder] = attachment['version']
	# 			# 	# save new PDF location to listfile
	# 			# 	with open('D:/LexBib/zot2wb/attachment_folders.csv', 'a', encoding="utf-8") as attachment_folder_listfile:
	# 			# 		attachment_folder_listfile.write(pdffolder+"\t"+str(attachment['version'])+"\n")
	# 			lwb.setqualifier(bibItemQid,"P16",zotitemstatement,"P70",pdffolder,"string")
	# 		elif attachment['contentType'] == "text/plain": # prefers cleantext or any other over grobidtext
	# 			txtloc = re.search(r'(D:\\Zotero\\storage)\\([A-Z0-9]+)\\(.*)', attachment['localPath']).group(2)
	# 			filetype = None
	# 			if "GROBID" not in attachment['title'] and "pdf2txt" not in attachment['title'] and "pdf2text" not in attachment['title']:
	# 				txtfolder = txtloc
	# 				txttype = "clean"
	# 			elif txttype != "clean" and "pdf2txt" not in attachment['title'] and "pdf2text" not in attachment['title']:
	# 				txtfolder = txtloc
	# 				txttype = "GROBID or other"
	# 	if txtfolder:
	# 		lwb.setqualifier(bibItemQid,"P16",zotitemstatement,"P71",txtfolder,"string")

	with open(outfilename, 'a', encoding="utf-8") as outfile:
		outfile.write(json.dumps({"lexBibID":bibItemQid})+'\n')
	print('Item finished.')
	itemcount += 1



#print(str(json.dumps(lwb_data)))
# with open(infile.replace('.json', '_lwb_import_data.json'), 'w', encoding="utf-8") as json_file: # path to result JSON file
#	json.dump(lwb_data, json_file, indent=2)
print("\n=============================================\nCreated processed JSON file "+infile.replace('.json', '_lwb_import_data.json')+". Finished.")
print("Now you probably will run bibimport, update placemapping, grobidupload\n")
# print('New places:')
# print(str(new_places))
# with open('newplaces.json', 'a', encoding="utf-8") as placesfile:
# 	json.dump(new_places, placesfile, indent=2)

# # save known wikipedia-wikidata mappings to file
# with open(config.datafolder+'mappings/wppage-wdid-mappings.json', 'w', encoding="utf-8") as mappingfile:
# 	json.dump(wikipairs, mappingfile, ensure_ascii=False, indent=2)
# print('\nsaved known Wikipedia-Wikdiata mappings.')
