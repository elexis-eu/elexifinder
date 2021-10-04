import json, time
from SPARQLWrapper import SPARQLWrapper, JSON

with open('D:/LexBib/doi/lexbib_doi.json', 'r', encoding="utf-8") as infile:
    bibdict = json.load(infile, encoding="utf-8")

joineddict = {}
wdquerycount = 0
for item in bibdict['results']['bindings']:
    doi = item['doi']['value']
    uri = item['uri']['value']
    title = item['title']['value']
    authorsJson = item['authorsJson']['value']
    joineddict[uri]={'doi':doi, 'lexbibtitle':title, 'lexbibauthors':json.loads(authorsJson)}


    if 'wikidata' not in item:

        #query wikidata
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent='LexBib-Bibliodata-enrichment-script (lexbib.org)')
        querya = """SELECT ?bibItem ?bibItemLabel ?authorUri ?authorUriLabel ?authorLiteral
                        WHERE
                        {
                          ?bibItem wdt:P356 """
        queryb = """.
                    OPTIONAL{?bibItem wdt:P50 ?authorUri.}
                    OPTIONAL{?bibItem wdt:P2093 ?authorLiteral.}
                    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
                    } limit 1"""
        sparql.setQuery(querya+'"'+doi+'"'+queryb)
        sparql.setReturnFormat(JSON)
        wdquerycount = wdquerycount + 1
        print('\n\n[attempt# '+str(wdquerycount)+']\n\n')
    #    try:
        time.sleep(1.5)
        wddict = sparql.query().convert()
        print(str(wddict))
        datalist = wddict['results']['bindings']
        if len(datalist) > 0:
            print(str(datalist))
            joineddict[uri]['wikidata'] = datalist


        else:
            joineddict[uri]['wikidata'] = 0


    else:
        print('This item is already in the dict: '+doi)



#        except Exception as ex:
#            print(" not found on wikidata, error for DOI: "+doi)
#            pass
with open('D:/LexBib/doi/lexbib_doi_wikidata.json', 'w', encoding="utf-8") as outfile:
    json.dump(joineddict, outfile, ensure_ascii=False, indent=2)

print('Finished. Performed wd queries: '+str(wdquerycount))
