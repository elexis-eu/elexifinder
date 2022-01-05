import requests, json, time

with open('D:/LexBib/elexifinder/elexifinder_api_key.txt') as pwdfile:
	EFapiKey = pwdfile.read()

EFhost = "http://finder.elex.is"

# params = {
#     "resultType": "articles",
#     "apiKey": EFapiKey
# }
#
# res = requests.get(EFhost + "/api/v1/article/getArticles", params)
#
# data = res.json()
# #print(str(data))
#
# results = data.get("articles", {}).get("results", [])
#
# with open('D:/LexBib/elexifinder/results.json', 'w', encoding="utf-8") as jsonfile:
# 	json.dump(results, jsonfile)

def chunks(lst, n):
	for i in range(0, len(lst), n):
		yield lst[i:i + n]

export_items = """Q9054
Q13618
Q10752
Q13279
Q12734
Q8693
Q12270
Q11845
Q15742
Q11229""".split("\n")
urilists = chunks(export_items, 1000)

#urilists = chunks(list(json.load(jsonfile).keys()), 1000)
print(str(urilists))

# params = {
#     "keyword": "examples",
#     "resultType": "articles",
#     "apiKey": EFapiKey
# }
#
# res = requests.get(EFhost + "/api/v1/article/getArticles", params)
#
# data = res.json()
# results = data.get("articles", {}).get("results", [])
#
# if len(results) > 0:
# 	# select a list of article uris to delete - in your case you can find the uris in some other way
# 	uris = [res["uri"] for res in results][:3]
#
# 	print(str(uris))
#
# 	removeParams = {
# 	    "articleUri": uris,
# 	    "forceImmediateDelete": True,
# 	    "apiKey": EFapiKey
# 	}
#
# 	res = requests.post(EFhost + "/api/admin/v1/articleAdmin/deleteArticle", json = removeParams)
# 	print(res.json())
# else:
# 	print('No results.')

for urilist in urilists:
	print(str(urilist))

	removeParams = {
	    "articleUri": urilist,
	    "forceImmediateDelete": True,
	    "apiKey": EFapiKey
	}

	res = requests.post(EFhost + "/api/admin/v1/articleAdmin/deleteArticle", json = removeParams)
	print(res.json())

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
