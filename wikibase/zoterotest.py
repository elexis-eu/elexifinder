import requests
import json
import config

attachment = [
{
"itemType": "attachment",
"parentItem": "QEW5IKYY",
"linkMode": "linked_url",
"title": "LexBib Linked Data",
"accessDate": "2021-08-08T00:00:00Z",
"url": "http://lexbib.elex.is/entity/Q1",
"note": '<p>See this item as linked data at</p><p><a href="http://lexbib.elex.is/entity/Q1">http://lexbib.elex.is/entity/Q1</a>',
"tags": [],
"collections": [],
"relations": {},
"contentType": "",
"charset": ""
}
]

r = requests.post('https://api.zotero.org/groups/1892855/items', headers={"Zotero-API-key":config.zotero_api_key, "Content-Type":"application/json"} , json=attachment)

print(str(r))
#print(str(r.content))
rjson = r.json()

with open('D:/LexBib/zoteroapi/examplenewlinkattach.json', "w", encoding="utf-8") as jsonfile:
	json.dump(rjson, jsonfile)
