# Post-processing of the output from LexBib_RDF.js.
# finds Wikipedia English page titles in RDF location property values and replaces them with wikidata uri
# saves known wikidata mappings in file
# lists places with metadata for elexifinder in csv
# exports PDF attachments to separate folder, for sending to GROBID, and lists them as exported in file
# by dlindem

from datetime import datetime
import re
import os
import requests
import wget
from w3lib.html import replace_entities
import json
import csv
import shutil
from SPARQLWrapper import SPARQLWrapper, JSON
import time
from rdflib import URIRef, Literal, Namespace, Graph

zotero_lexbib_rdf_export_file = 'D:/LexBib/exports/LEXICONORDICA.rdf'

with open(zotero_lexbib_rdf_export_file, 'r', encoding="utf-8") as infile:
    exportlines = infile.readlines()

try:
    with open('D:/LexBib/exported_PDF_list.json', 'r', encoding="utf-8") as pdflistfile:
        pdflist = json.load(pdflistfile, encoding="urf-8")
except:
    print('\npdflistfile not there, will save in a new one.')
    pdflist = {}



#print(exportlines)

try:
    with open('D:/LexBib/wppage-wdid-mappings.json', encoding="utf-8") as f:
    	wikipairs =  json.load(f, encoding="utf-8")
except:
    wikipairs = {}

with open(os.path.splitext(zotero_lexbib_rdf_export_file)[0]+"_wikidata.rdf", 'w', encoding="utf-8") as outfile:
    for line in exportlines:
        aulocmatch = re.search('([^<]*)<lexdo:firstAuLoc>https?://en.wikipedia.org/wiki/([^<]+)</lexdo:firstAuLoc>', line)
        arlocmatch = re.search('([^<]*)<lexdo:articleLoc>https?://en.wikipedia.org/wiki/([^<]+)</lexdo:articleLoc>', line)
        pdfmatch = re.search('[^<]*<zotexport:pdfFile>(D:/Zotero/storage/[^<]+)</zotexport:pdfFile>', line) # Zotero storage folder path / attachment folder / filename.pdf
        if "'" in pdfmatch:
            print("PDF file "+pdfmatch+" will be renamed (remove single quote from name)")
            line = line.replace("'", "")
            os.rename(pdfmatch, pdfmatch.replace("'", ""))
            pdfmatch = pdfmatch.replace("'", "")
        if aulocmatch != None:
            wppage = (aulocmatch.group(2))
            if wppage not in wikipairs:
                wdjsonsource = requests.get(url='https://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&format=json&titles='+wppage)
                wdjson =  wdjsonsource.json()
                entities = wdjson['entities']
                for wdid in entities:
                    print("found new wdid "+wdid+" for AUTHORLOC "+wppage)
                    line = aulocmatch.group(1)+'<lexdo:firstAuLoc rdf:resource="http://www.wikidata.org/entity/'+wdid+'"/>\n'
                    wikipairs[wppage] = wdid
            else:
                wdid = wikipairs[wppage]
                line = aulocmatch.group(1)+'<lexdo:firstAuLoc rdf:resource="http://www.wikidata.org/entity/'+wdid+'"/>\n'
                print("used known wdid "+wdid+" for AUTHORLOC "+wppage)
        if arlocmatch != None:
            #print(arlocmatch.group(2))
            wppage = (arlocmatch.group(2))
            if wppage not in wikipairs:
                wdjsonsource = requests.get(url='https://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&format=json&titles='+wppage)
                wdjson =  wdjsonsource.json()
                entities = wdjson['entities']
                for wdid in entities:
                    print("found new wdid "+wdid+" for ARTICLELOC "+wppage)
                    line = arlocmatch.group(1)+'<lexdo:articleLoc rdf:resource="http://www.wikidata.org/entity/'+wdid+'"/>\n'
                    wikipairs[wppage] = wdid
            else:
                wdid = wikipairs[wppage]
                line = arlocmatch.group(1)+'<lexdo:articleLoc rdf:resource="http://www.wikidata.org/entity/'+wdid+'"/>\n'
                print("used known wdid " +wdid+" for ARTICLELOC "+wppage)
        if pdfmatch != None:
            pdffile = replace_entities(pdfmatch.group(1))
            print(pdffile)
            attachfolder = re.search('D:/Zotero/storage/([A-Z0-9]+)/(.*)', pdffile)
            print(attachfolder.group(1))
            if pdffile in pdflist:
                print('This file has been exported at '+pdflist[pdffile]+': '+pdffile)
            else:
                newpath = 'D:/LexBib/exports/exported_files/'+attachfolder.group(1)
                if not os.path.isdir(newpath):
                    os.makedirs(newpath)
                shutil.copy('D:/Zotero/storage/'+attachfolder.group(1)+'/'+attachfolder.group(2), newpath+'/'+attachfolder.group(2))
                print('Found and copied '+pdffile)
                pdflist[pdffile] = str(datetime.now())
                print(pdflist[pdffile])

        outfile.write(line)

# save updated PDF list
with open('D:/LexBib/exported_PDF_list.json', 'w', encoding="utf-8") as pdflistfile:
    json.dump(pdflist, pdflistfile, ensure_ascii=False, indent=2)

# save known wikipedia-wikidata mappings to file
with open('D:/LexBib/wppage-wdid-mappings.json', 'w', encoding="utf-8") as mappingfile:
	json.dump(wikipairs, mappingfile, ensure_ascii=False, indent=2)
print('\nsaved knwon Wikipedia-Wikdiata mappings.')

# update lexplaces.json
try:
    with open('D:/LexBib/lexplaces.json', encoding="utf-8") as lexplacefile:
        lpdict =  json.load(lexplacefile, encoding="utf-8")
        print("\nloaded lexplacefile\n")
except:
    lpdict = {}
    print("\ncreated new lexplacefile\n")
wdquerycount = 0
wdsucc = 0
for mapping in wikipairs:
    if wikipairs[mapping] not in lpdict:
        print(mapping+" "+wikipairs[mapping]+" not found in lexplacefile, will query wikidata")
        wdid = wikipairs[mapping]

        #query wikidata
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent='LexBib-Bibliodata-enrichment-script (lexbib.org)')
        sparql.setQuery("""SELECT ?label ?country ?countrylabel
                    WHERE {
                        wd:"""+wdid+""" rdfs:label ?label .
                        FILTER (langMatches( lang(?label), "EN" ) )
                        wd:"""+wdid+""" wdt:P17 ?country.
                        ?country rdfs:label ?countrylabel .
                        FILTER (langMatches( lang(?countrylabel), "EN" ) )
                        } limit 1""")
        sparql.setReturnFormat(JSON)
        wdquerycount = wdquerycount + 1
        try:
            time.sleep(1.5)
            wddict = sparql.query().convert()
            datalist = wddict['results']['bindings']
            print(datalist[0])
            countryNode = datalist[0]['country']['value']
            countrylabel = datalist[0]['countrylabel']['value']
            citylabel = datalist[0]['label']['value']
            print(countrylabel+" / "+countryNode+" / "+citylabel)
            wpurl = "http://en.wikipedia.org/wiki/"+mapping
            print(wpurl)
            lpdict[wdid] = {"wpurl":wpurl, "country":countryNode, "countrylabel":countrylabel, "citylabel":citylabel}
            wdsucc = wdsucc + 1

        except Exception as ex:
            print(mapping+" "+wikipairs[mapping]+" not found on wikidata, error: "+str(ex))
            pass
    else:
        print(mapping+" "+wikipairs[mapping]+" found in lexplacefile, no wikidata query needed")

print("\nTried to perform "+str(wdquerycount)+" wikidata queries. Actually retrieved "+str(wdsucc)+" answers from Wikidata.")
#print(lpdict)
with open('D:/LexBib/lexplaces.json', 'w', encoding="utf-8") as json_file:
	json.dump(lpdict, json_file, ensure_ascii=False, indent=2)
print("\nlexplacefile json updated.")

gn = Namespace('http://www.geonames.org/ontology#')
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
schema = Namespace ('http://schemas.talis.com/2005/address/schema#')
wd = Namespace ('http://www.wikidata.org/entity/')
lexdotop = Namespace ('http://lexbib.org/lexdo-top/')

placesgraph = Graph()
placesgraph.bind("gn", gn)
placesgraph.bind("skos", skos)
placesgraph.bind("rdf", rdf)
placesgraph.bind("schema", schema)
placesgraph.bind("wd", wd)
placesgraph.bind("lexdo-top", lexdotop)

for wdplace, placedata in lpdict.items():
    #print(wdplace)
    #print(placedata)
    placenode = URIRef('http://www.wikidata.org/entity/'+wdplace)
    countrynode = URIRef(placedata['country'])
    countrylabel = Literal(placedata['countrylabel'])
    citylabel = Literal(placedata['citylabel'])
    wpurl = URIRef(placedata['wpurl'])
    placesgraph.add((placenode, rdf.type, schema.City))
    placesgraph.add((placenode, rdf.type, lexdotop.Place))
    placesgraph.add((placenode, schema.containedInPlace, countrynode))
    placesgraph.add((placenode, gn.wikipediaArticle, wpurl))
    placesgraph.add((placenode, skos.prefLabel, citylabel))
    placesgraph.add((countrynode, rdf.type, schema.Country))
    placesgraph.add((countrynode, skos.prefLabel, countrylabel))

placesgraph.serialize(destination="D:/LexBib/lexplaces.ttl", format="turtle")

print("Lexplaces TTL file updated.")

with open("D:/LexBib/lexplaces.csv", "w", encoding="utf-8", newline="") as csv_file:
    f = csv.writer(csv_file, delimiter="\t", lineterminator="\n")
    f.writerow(["Wikidata URI", "gn:wikipediaArticle", "rdfs:label@en", "schema:containedInPlace", "countryLabel"])
    for place in lpdict:
        f.writerow(["http://www.wikidata.org/entity/"+place, lpdict[place]['wpurl'], lpdict[place]['citylabel'], lpdict[place]['country'], lpdict[place]['countrylabel']])
print("lexplacefile csv updated, finished.")
