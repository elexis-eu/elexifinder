# PREFIX : <http://lexbib.org/lexdo/>
# PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
# PREFIX zotexport: <http://www.zotero.org/namespaces/export#>
# SELECT ?uri ?pdffiles
# ?abstractlang ?abstracttext
#
# where {
# 	?uri  :abstract ?abstractnode .
#     ?uri :zoteroItemUri ?zotitemnode .
#     OPTIONAL {?zotitemnode zotexport:pdfFile ?pdffiles .}
#     OPTIONAL{ ?abstractnode :abstractText ?abstracttext . }
#     OPTIONAL{ ?abstractnode :abstractLanguage ?abstractlanguri .}
#
# }
# GROUP BY ?uri ?pdffiles (STRAFTER( str(?abstractlanguri), "iso639-3/" ) as ?abstractlang) ?abstracttext

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
