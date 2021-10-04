import requests
import json
import time
import hashlib
import config
import sys
from datetime import datetime
#from pyzotero import zotero

# load bodytxt collection
with open('D:/LexBib/bodytxt/bodytxt_collection.json', encoding="utf-8") as infile:
	bodytxtcoll = json.load(infile)

with open(config.datafolder+'zoteroapi/zotero_api_key.txt', 'r', encoding='utf-8') as pwdfile:
	zotero_api_key = pwdfile.read()

#zotapi = zotero.Zotero(1892855, 'group', zotero_api_key)

with open('D:/LexBib/bodytxt/grobid_txt_attachment_log.log', "r") as logfile:
	doneqid = logfile.read().split('\n')

# r = requests.patch('https://api.zotero.org/groups/1892855/items/WLSRE47G', headers={"If-Unmodified-Since-Version":"73527", "Zotero-API-key":zotero_api_key}, json={"archiveLocation":"http://data.lexbib.org/entity/Q1698"})
#r = requests.get('https://api.zotero.org/items/new', headers={"Zotero-API-key":zotero_api_key} , params={"itemType":"attachment","linkMode":"imported_file"})


# attachment = [
#   {
#     "itemType": "attachment",
#     "parentItem": "ABCD2345",
#     "linkMode": "imported_url",
#     "title": "My Document",
#     "accessDate": "2012-03-14T17:45:54Z",
#     "url": "http://example.com/doc.pdf",
#     "note": "",
#     "tags": [],
#     "relations": {},
#     "contentType": "application/pdf",
#     "charset": "",
#     "filename": "doc.pdf",
#     "md5": null,
#     "mtime": null
#   }
# ]

# attachment = [
# {
# "itemType": "attachment",
# "parentItem": "7MNFBCDZ",
# "linkMode": "linked_url",
# "title": "Podio Link",
# "accessDate": "2012-03-14T17:45:54Z",
# "url": "https://thelink.com",
# "note": "",
# "tags": [],
# "collections": [],
# "relations": {},
# "contentType": "",
# "charset": ""
# }
# ]

#r = requests.post('https://api.zotero.org/groups/1892855/items', headers={"Zotero-API-key":zotero_api_key, "Content-Type":"application/json"} , json=attachment)

for qid in bodytxtcoll:
	if qid in doneqid:
		print('\n'+qid+" has been processed already, skipped.")
		continue
	if bodytxtcoll[qid]['source'] != "grobid":
		#print('\n'+qid+' is not GROBID text, skipped.')
		continue

	zotid = bodytxtcoll[qid]['zotItem'].replace("http://lexbib.org/zotero/","")
	bodytxt = bodytxtcoll[qid]['bodytxt'].encode("utf-8", errors="ignore")
	#bodytxt = "Hallo das ist mein Text-Text und lorem ipsum undsoweiter@@@!!!ááá"
	md5 = hashlib.md5()
	md5.update(bodytxt)
	md5_hash = md5.hexdigest()
	mtime = time.time_ns() // 1_000_000
	#mtime = round(time.time() * 1000)
	txtsize = len(bodytxt)
	print('\nWill now process: ',qid, zotid, str(txtsize), mtime, md5_hash)

	#zotapi.attachment_simple(['D:/LexBib/bodytxt/upload.txt'],zotid)

	#sys.exit()


	# attach new grobid-produced text body to zotero item
	attachment = [
	{
	"itemType": "attachment",
	"parentItem": zotid,
	"linkMode": "imported_file",
	"title": "GROBID text body",
	"accessDate": "",
	"note": "",
	"tags": [], # [{'tag':'grobid_upload'}],
	"collections": [],
	"relations": {},
	"contentType": "",
	"charset": "",
	"filename": ""
	}
	]
	# create new attachment item
	r = requests.post('https://api.zotero.org/groups/1892855/items', headers={"Zotero-API-key":zotero_api_key, "Content-Type":"application/json"} , json=attachment)

	print(str(r))
	#print(str(r.content))
	rjson = r.json()

	with open('D:/LexBib/zoteroapi/examplenewfileattach.json', "w", encoding="utf-8") as jsonfile:
		json.dump(rjson, jsonfile)

	if "success" in rjson:
		att_key = rjson['successful']['0']['key']
		print("New attachment will have key "+att_key)
	time.sleep(1)

	# r1 = requests.get('https://api.zotero.org/groups/1892855/items/'+att_key)
	#
	# print(str(r1))
	# print(str(r1.content))
	# print(str(r1.json()))
	#
	# with open('D:/LexBib/zoteroapi/r1.json', "w", encoding="utf-8") as jsonfile:
	# 	json.dump(r1.json(), jsonfile)
	# zjson={
	# "md5": md5_hash,
	# "filename": zotid+"_grobidbody.txt",
	# "filesize": str(txtsize),
	# "mtime": str(mtime),
	# "contentType": "application/octet-stream",
	# "charset": "utf-8",
	# }
	# jsondata="md5="+md5_hash+"&filename="+zotid+"_grobidbody.txt&filesize="+str(txtsize)+"&mtime="+str(mtime)+"&contentType=text/plain"
	#
	# print(jsondata)

	upload_perm = requests.post('https://api.zotero.org/groups/1892855/items/'+att_key+'/file',
	headers = {
	"Zotero-API-key":zotero_api_key,
	"Content-Type":"application/x-www-form-urlencoded",
	"If-None-Match":"*"
	},
	data = "md5="+md5_hash+"&filename="+zotid+"_grobidbody.txt&filesize="+str(txtsize)+"&mtime="+str(mtime)
	)

	print(str(upload_perm))
	#print(str(upload_perm.content))
	#print(str(upload_perm.json()))

	with open('D:/LexBib/zoteroapi/exampleuploadperm.json', "w", encoding="utf-8") as jsonfile:
		json.dump(upload_perm.json(), jsonfile)
	upload_perm = upload_perm.json()

	if "exists" in upload_perm and upload_perm['exists'] == 1:
		print('This text is already on the server. Associated as new attachment.')
		with open('D:/LexBib/bodytxt/grobid_txt_attachment_log.log', "a") as logfile:
			logfile.write(qid+'\n')

		continue

	upload = requests.post(upload_perm['url'], headers={"content-type":upload_perm['contentType']}, data=upload_perm['prefix'].encode('utf-8')+bodytxt+upload_perm['suffix'].encode('utf-8'))
	time.sleep(1)

	registration = requests.post('https://api.zotero.org/groups/1892855/items/'+att_key+'/file',
	headers = {
	"Zotero-API-key":zotero_api_key,
	"Content-Type":"application/x-www-form-urlencoded",
	"If-None-Match":"*"
	},
	data = "upload="+upload_perm['uploadKey']
	)

	print(str(registration))

	with open('D:/LexBib/bodytxt/grobid_txt_attachment_log.log', "a") as logfile:
		logfile.write(qid+'\n')
