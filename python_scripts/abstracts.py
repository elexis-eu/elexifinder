import json, time, re


with open('D:/LexBib/abstracts/query-result.srj', 'r', encoding="utf-8") as infile:
    sparqldict = json.load(infile, encoding="utf-8")['results']['bindings']
absdict = {}
for item in sparqldict:
    abstracttext = ""
    abstractlang = None
    if 'uri' in item:
        uri = item['uri']['value']
        print(uri)
    if 'abstracttext' in item:
        abstracttext = item['abstracttext']['value']
    if 'abstractlang' in item:
        abstractlang = item['abstractlang']['value']
    if abstracttext != "":
        absdict[uri]={'text':abstracttext, 'lang':abstractlang}


with open('D:/LexBib/abstracts/abstracts.json', 'w', encoding="utf-8") as outfile:
    json.dump(absdict, outfile, ensure_ascii=False, indent=2)
