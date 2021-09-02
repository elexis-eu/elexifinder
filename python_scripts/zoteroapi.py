import requests
import json
import time

zotero_api_key = "Qlm9o2ZkCaYrtzCQ5d5XjwCx"


# r = requests.patch('https://api.zotero.org/groups/1892855/items/WLSRE47G', headers={"If-Unmodified-Since-Version":"73527", "Zotero-API-key":"Qlm9o2ZkCaYrtzCQ5d5XjwCx"}, json={"archiveLocation":"http://data.lexbib.org/entity/Q1698"})
#r = requests.get('https://api.zotero.org/items/new', headers={"Zotero-API-key":"Qlm9o2ZkCaYrtzCQ5d5XjwCx"} , params={"itemType":"attachment","linkMode":"imported_file"})


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

#r = requests.post('https://api.zotero.org/groups/1892855/items', headers={"Zotero-API-key":"Qlm9o2ZkCaYrtzCQ5d5XjwCx", "Content-Type":"application/json"} , json=attachment)

# attach new grobid-produced text body to zotero item



attachment = [
{
"itemType": "attachment",
"parentItem": "WLSRE47G",
"linkMode": "imported_file",
"title": "GROBID text body",
"accessDate": "",
"note": "",
"tags": [],
"collections": [],
"relations": {},
"contentType": "text/plain",
"charset": "utf-8",
"filename": "hallonewtxt.txt"
}
]

r = requests.post('https://api.zotero.org/groups/1892855/items', headers={"Zotero-API-key":zotero_api_key, "Content-Type":"application/json"} , json=attachment)

print(str(r))
print(str(r.content))
rjson = r.json()


with open('D:/LexBib/zoteroapi/examplenewfileattach.json', "w", encoding="utf-8") as jsonfile:
	json.dump(rjson, jsonfile)

if "success" in rjson:
	att_key = rjson['successful']['0']['key']
	print("New attachment will have key "+att_key)
time.sleep(4)

# r1 = requests.get('https://api.zotero.org/groups/1892855/items/'+att_key)
#
# print(str(r1))
# print(str(r1.content))
# print(str(r1.json()))
#
# with open('D:/LexBib/zoteroapi/r1.json', "w", encoding="utf-8") as jsonfile:
# 	json.dump(r1.json(), jsonfile)


r2 = requests.post('https://api.zotero.org/groups/1892855/items/'+att_key+'/file', headers={"Zotero-API-key":zotero_api_key,"Content-Type":"application/x-www-form-urlencoded", "If-None-Match":"*", "params":"1"}, json={"md5":"filename=hallonewtxt.txt", "params":"1"})





print(str(r2))
print(str(r2.content))
print(str(r2.json()))

with open('D:/LexBib/zoteroapi/r2.json', "w", encoding="utf-8") as jsonfile:
	json.dump(r2.json(), jsonfile)

#r = requests.patch('https://httpbin.org / patch', data ={'key':'value'})



vorlage = {
				"version": 77086,
				"itemType": "attachment",
				"url": "http://data.lexbib.org/entity/Q1698",
				"accessDate": "2021-03-15T17:11:57Z",
				"title": "LexBib item",
				"parentItem": "WLSRE47G",
				"linkMode": "linked_url",
				"contentType": "",
				"charset": "",
				"tags": [],
				"relations": {},
				"dateAdded": "2021-03-15T17:11:57Z",
				"dateModified": "2021-03-15T17:11:57Z",
				"uri": "http://zotero.org/groups/1892855/items/6S4CAK2Q"
			}
