# Post-processing of the output from LexBib_RDF.js.
# finds Wikipedia English page titles in RDF location property values and replaces them with wikidata uri
# saves known wikidata mappings in file
# lists places with metadata for elexifinder in csv
# exports PDF attachments to separate folder, for sending to GROBID, and lists them as exported in file
# by dlindem

from datetime import datetime
import sys
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
from rdflib import Graph, Namespace, BNode, URIRef, Literal
from unidecode import unidecode
from tkinter import Tk
from tkinter.filedialog import askopenfilename

with open('eventlist.csv', encoding="utf-8") as csvfile: # event mapping csv
    eventdict = csv.DictReader(csvfile, delimiter="\t")
    eventkeydict = {}
    for item in eventdict:
        eventkeydict[item['LexBibUri']] = item['place']


Tk().withdraw()
zotero_lexbib_rdf_export_file = askopenfilename()
print('File to process is '+zotero_lexbib_rdf_export_file)

try:
    #time.sleep(1)
    with open(zotero_lexbib_rdf_export_file, 'r', encoding="utf-8") as infile:
        exportlines = infile.readlines()
    infiletime = str(datetime.fromtimestamp(os.path.getmtime(zotero_lexbib_rdf_export_file)))[0:22].replace(' ','T')
    print('File found. Will start to process.')
    #time.sleep(1)
except:
    print('File not found')
    sys.exit()

print('Which version is this? Type the number.')

try:
    version = int(input())
    print ('OK, version is '+str(version)+', will start to process...')
except:
    print ('Error: This has to be a number.')
    sys.exit()

try:
    with open('D:/LexBib/journals/journals.json', 'r', encoding="utf-8") as infile:
        issndict = json.load(infile, encoding="utf-8")
except:
    print('\njournalfile not there, will save in a new one.')
    issndict = {}

try:
    with open('D:/LexBib/exports/exported_PDF.json', 'r', encoding="utf-8") as pdflistfile:
        pdflist = json.load(pdflistfile, encoding="utf-8")
except:
    print('\npdflistfile not there, will save in a new one.')
    pdflist = {}

errorlog = []


#print(exportlines)

try:
    with open('D:/LexBib/places/wppage-wdid-mappings.json', encoding="utf-8") as f:
    	wikipairs =  json.load(f, encoding="utf-8")
except:
    wikipairs = {}
interimfile = os.path.splitext(zotero_lexbib_rdf_export_file)[0]+"_pp_v"+str(version)+".rdf"
with open(interimfile, 'w', encoding="utf-8") as tmpfile:
    for line in exportlines:
        authormatch = re.search('(.*\")(http://lexbib.org/agents/person/)([^\"]+)(\".*)', line)
        aulocmatch = re.search('([^<]*)<lexdo:firstAuLoc>https?://en.wikipedia.org/wiki/([^<]+)</lexdo:firstAuLoc>', line)
        arlocmatch = re.search('([^<]*)<lexdo:event rdf:resource=\"(http[^\"]+)\"/>', line)
        pdfmatch = re.search('([^<]*<zotexport:pdfFile>)(D:/Zotero/storage)/([A-Z0-9]+)/([^<]+)(</zotexport:pdfFile>.*)', line) # Zotero storage folder path / attachment folder / filename.pdf
        pdf2textmatch = re.search('[^<]*<zotexport:txtFile>D:/Zotero/storage/[^\/]+/pdf2text.txt</zotexport:txtFile>.*', line)
        issnmatch = re.search('[^<]*<bibo:issn>([^<]+)</bibo:issn>.*', line)
        if pdf2textmatch != None:
            line = "" # eliminates manually added pdf2text attachments (visible and syncable duplicates of .zotero-ft-cache file)
        if authormatch != None:
            author = authormatch.group(3)
            author = re.sub(r'[^A-Za-z:/]', '', unidecode(author))
            #print (author)
            line = authormatch.group(1)+authormatch.group(2)+author+authormatch.group(4)
        if aulocmatch != None:
            wppage = (aulocmatch.group(2))
            if wppage not in wikipairs:
                wdjsonsource = requests.get(url='https://www.wikidata.org/w/api.php?action=wbgetentities&sites=enwiki&format=json&titles='+wppage)
                wdjson =  wdjsonsource.json()
                entities = wdjson['entities']
                for wdid in entities:
                    #print("found new wdid "+wdid+" for AUTHORLOC "+wppage)
                    line = aulocmatch.group(1)+'<lexdo:firstAuLoc rdf:resource="http://www.wikidata.org/entity/'+wdid+'"/>\n'
                    wikipairs[wppage] = wdid
            else:
                wdid = wikipairs[wppage]
                line = aulocmatch.group(1)+'<lexdo:firstAuLoc rdf:resource="http://www.wikidata.org/entity/'+wdid+'"/>\n'
                #print("used known wdid "+wdid+" for AUTHORLOC "+wppage)

        if arlocmatch != None:
            #print(arlocmatch.group(2))
            eventurl = (arlocmatch.group(2))
            if eventurl in eventkeydict:
                wdid = eventkeydict[eventurl] # gets event location from eventlist mapping
            else:
                print("WARNING: event "+eventurl+" NOT FOUND in event uri-place dictionary!")
                time.sleep(10)
            line = arlocmatch.group(0)+'\n        <lexdo:articleLoc rdf:resource="http://www.wikidata.org/entity/'+wdid+'"/>\n'
            print("used known wdid " +wdid+" for EVENT LOCATION of "+eventurl)
        if pdfmatch != None:
            pdffolder = pdfmatch.group(3)
            pdfoldfile = pdfmatch.group(4)
            forbidden = re.compile(r'[^a-zA-Z0-9_\.]')
            if forbidden.search(pdfoldfile):
                #print("PDF file "+pdfoldfile+" will be renamed (remove [^a-zA-Z0-9_] from name)")
                pdfnewfile = forbidden.sub('', pdfoldfile)
                #line = pdfmatch.group(1)+pdfmatch.group(2)+pdfoldpath+pdfnewfile+pdfmatch.group(4)
                #print('Renamed PDF file to handle is '+pdfnewfile)
                #time.sleep(1)
            else:
                pdfnewfile = pdfoldfile
                #print('PDF file to handle is '+pdfnewfile)
            if pdffolder+'/'+pdfnewfile not in pdflist:
                newpath = 'D:/LexBib/exports/export_filerepo/'+pdffolder
                if not os.path.isdir(newpath):
                    os.makedirs(newpath)
                shutil.copy('D:/Zotero/storage/'+pdffolder+'/'+pdfoldfile, newpath+'/'+pdfnewfile)
                print('Found and copied '+pdfnewfile)
                pdflist[pdffolder+'/'+pdfnewfile] = infiletime+'_'+zotero_lexbib_rdf_export_file+'_v'+str(version)
                #print(pdflist[pdfnewfile])
        if issnmatch != None:
            issn = issnmatch.group(1).split(',')[0]
            if issn in issndict:
                journal = issndict[issn]['qid']
            #    print("found known issn")
            else:
                # get journal Qid from wikidata

                sparql = SPARQLWrapper("https://query.wikidata.org/sparql", agent='LexBib-Bibliodata-enrichment-script (lexbib.org)')
                sparql.setQuery('SELECT ?journal ?journalLabel WHERE {?journal wdt:P236 '+'"'+issn+'"'+'. SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}')
                sparql.setReturnFormat(JSON)

                try:
                    time.sleep(1.5)
                    wddict = sparql.query().convert()
                    datalist = wddict['results']['bindings']
                    print('\nGot ISSN '+issn+' data from Wikidata:\n'+str(datalist[0]))
                    journal = datalist[0]['journal']['value']
                    issndict[issn]={'qid':journal, 'title':datalist[0]['journalLabel']['value']}

                except Exception as ex:
                    print("ISSN "+issn+" not found on wikidata, skipping. >> "+str(ex))
                    pass
            line=issnmatch.group(0)+'\n        <lexdo:journal rdf:resource="'+journal+'"/>\n'

        tmpfile.write(line)

# save updated PDF list
with open('D:/LexBib/exports/exported_PDF.json', 'w', encoding="utf-8") as pdflistfile:
    json.dump(pdflist, pdflistfile, ensure_ascii=False, indent=2)

# save known wikipedia-wikidata mappings to file
with open('D:/LexBib/places/wppage-wdid-mappings.json', 'w', encoding="utf-8") as mappingfile:
	json.dump(wikipairs, mappingfile, ensure_ascii=False, indent=2)
print('\nsaved known Wikipedia-Wikdiata mappings.')

# update lexplaces.json
try:
    with open('D:/LexBib/places/lexplaces.json', encoding="utf-8") as lexplacefile:
        lpdict =  json.load(lexplacefile, encoding="utf-8")
        print("\nloaded lexplacefile\n")
except:
    lpdict = {}
    print("\ncreated new lexplacefile\n")
wdquerycount = 0
wdsucc = 0
for mapping in wikipairs:
    if 'Q' in wikipairs[mapping] and wikipairs[mapping] not in lpdict:
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
            errorlog.append({wdid:str(ex)})
            pass
    #else:
        #print(mapping+" "+wikipairs[mapping]+" found in lexplacefile, no wikidata query needed")

print("\nTried to perform "+str(wdquerycount)+" wikidata queries. Actually retrieved "+str(wdsucc)+" answers from Wikidata.")
#print(lpdict)
with open('D:/LexBib//places/lexplaces.json', 'w', encoding="utf-8") as json_file:
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

placesgraph.serialize(destination="D:/LexBib/places/lexplaces.ttl", format="turtle")

print("Lexplaces TTL file updated.")

with open("D:/LexBib/places/lexplaces.csv", "w", encoding="utf-8", newline="") as csv_file:
    f = csv.writer(csv_file, delimiter="\t", lineterminator="\n")
    f.writerow(["Wikidata URI", "gn:wikipediaArticle", "rdfs:label@en", "schema:containedInPlace", "countryLabel"])
    for place in lpdict:
        f.writerow(["http://www.wikidata.org/entity/"+place, lpdict[place]['wpurl'], lpdict[place]['citylabel'], lpdict[place]['country'], lpdict[place]['countrylabel']])
print("lexplacefile csv updated, finished.")

if len(errorlog) > 0:
    print('Error log is saved as wikidata_error.log')
    with open("D:/LexBib/places/wikidata_error.log", "w", encoding="utf-8") as errorfile:
        json.dump(errorlog, errorfile, ensure_ascii=False, indent=2)

print('Begin person information treatment and TTL export...')

try:
    with open('D:/LexBib/persons/lexpersons.json', encoding="utf-8") as f:
    	authorsdic =  json.load(f, encoding="utf-8")
except:
    print('\ncreatorlistfile not there, will save in a new one.')
    authorsdic = {}


g = Graph()

gn = Namespace('http://www.geonames.org/ontology#')
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
dcterms = Namespace ('http://purl.org/dc/terms/')
wd = Namespace ('http://www.wikidata.org/entity/')
foaf = Namespace ('http://xmlns.com/foaf/0.1/')
skosxl = Namespace('http://www.w3.org/2008/05/skos-xl#')

g.bind("gn", gn)
g.bind("skos", skos)
g.bind("rdf", rdf)
g.bind("dcterms", dcterms)
g.bind("wd", wd)
g.bind("foaf", foaf)
g.bind("skosxl", skosxl)

g.parse(interimfile, format="xml")

authors = g.query(
    """select DISTINCT ?lexdo_Person ?foaf_firstname ?foaf_surname ?skosxl_literalForm ?dct_source where {
	   ?lexdo_Person rdf:type lexdo:Person .
       ?lexdo_Person skosxl:altLabel ?personLabel .
       ?personLabel foaf:firstName ?foaf_firstname
                ; foaf:surname ?foaf_surname
    			; skosxl:literalForm ?skosxl_literalForm
                ; dcterms:source ?dct_source .


     } """)


for row in authors:
    if str(row.lexdo_Person) not in authorsdic:
        authorsdic[str(row.lexdo_Person)] = {str(row.dct_source):{'foaf_firstname' : str(row.foaf_firstname), 'foaf_surname' : str(row.foaf_surname), 'skosxl_literalForm' : str(row.skosxl_literalForm)}}
    else:
        authorsdic[str(row.lexdo_Person)].update({str(row.dct_source):{'foaf_firstname' : str(row.foaf_firstname), 'foaf_surname' : str(row.foaf_surname), 'skosxl_literalForm' : str(row.skosxl_literalForm)}})

#print(authorsdic)
with open('D:/LexBib/persons/lexpersons.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(authorsdic, json_file, indent=2)
print('Updated lexpersons.json')

print ('...creating csv for person data post-processing')

authordic = {}
for authoruri in authorsdic:
    #print(authordic[authoruri])
    if authoruri not in authordic:
        authordic[authoruri] = {}
    seen = []
    for puburi in authorsdic[authoruri]:
    #print(authorsdic[authoruri][puburi]['skosxl_literalForm'])
        literal = authorsdic[authoruri][puburi]['skosxl_literalForm']
        #print(literal)
        if len(authordic[authoruri]) > 0 : # if this author already has labels
            #print(authoruri+' already has labels')
            #for valuelist in authordic[authoruri]:
            #    if valuelist['skosxl_literalForm'] not in seen:
            if literal in seen:
                authordic[authoruri][literal]['count'] += 1

            else:
                authordic[authoruri][literal] = {"foaf_firstname":authorsdic[authoruri][puburi]['foaf_firstname'], "foaf_surname":authorsdic[authoruri][puburi]['foaf_surname'], "count" : 1}
                seen.append(literal)
        else: # if this author still has no labels
            authordic[authoruri][literal] = {"foaf_firstname":authorsdic[authoruri][puburi]['foaf_firstname'], "foaf_surname":authorsdic[authoruri][puburi]['foaf_surname'], "count" : 1}
            seen.append(literal)
    #for autlabel in seen:
        #print(autlabel)

with open('D:/LexBib/persons/authordic.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(authordic, json_file, indent=2)
print('Updated authordic.json')

with open("D:/LexBib/persons/lexpersons.csv", "w", encoding="utf-8", newline="") as csv_file:
    f = csv.writer(csv_file, delimiter="\t", lineterminator="\n")
    f.writerow(["lexdo_Person", "skosxl_literalForm", "foaf_firstname", "foaf_surname", "count"])
    for authoruri in authordic:
        for label in authordic[authoruri]:
            #print(valuelist)
            f.writerow([authoruri, label, authordic[authoruri][label]['foaf_firstname'], authordic[authoruri][label]['foaf_surname'], authordic[authoruri][label]['count']])
print("lexperson csv updated, finished.")

print("Will now update lexpersons.ttl...")

ag = Graph()

gn = Namespace('http://www.geonames.org/ontology#')
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
dcterms = Namespace ('http://purl.org/dc/terms/')
wd = Namespace ('http://www.wikidata.org/entity/')
foaf = Namespace ('http://xmlns.com/foaf/0.1/')
skosxl = Namespace('http://www.w3.org/2008/05/skos-xl#')
lexdo = Namespace('http://lexbib.org/lexdo/')
lexperson = Namespace('http://lexbib.org/agents/person/')

ag.bind("gn", gn)
ag.bind("skos", skos)
ag.bind("rdf", rdf)
ag.bind("dcterms", dcterms)
ag.bind("wd", wd)
ag.bind("foaf", foaf)
ag.bind("skosxl", skosxl)
ag.bind("lexdo", lexdo)
ag.bind("lexperson", lexperson)


for authoruri in authordic:
    #print(authorsdic[authoruri])
    author = URIRef(authoruri)
    ag.add((author, rdf.type, lexdo.Person))
    count = 0
    #seenlabels = []
    labelcount = {}
    for label in authordic[authoruri]:
        labelnode = BNode()
        ag.add((labelnode, rdf.type, skosxl.Label))
        ag.add((author, skosxl.altLabel, labelnode))
        ag.add((labelnode, foaf.firstName, Literal(authordic[authoruri][label]['foaf_firstname'])))
        ag.add((labelnode, foaf.surname, Literal(authordic[authoruri][label]['foaf_surname'])))
        ag.add((labelnode, skosxl.literalForm, Literal(label)))
        ag.add((labelnode, lexdo.nameVarFreq, Literal(authordic[authoruri][label]['count'])))
        labelcount[labelnode]=authordic[authoruri][label]['count']
    #print(labelcount)
    max_label = max(labelcount, key=labelcount.get)
    #print(max_label)
    ag.remove((author, skosxl.altLabel, max_label))
    ag.add((author, skosxl.prefLabel, max_label))

ag.serialize(destination='D:/LexBib/persons/lexpersons.ttl', format="turtle")


print ('...now removing Person data from infile RDF, saving result as .TTL, ready for upload to Ontotext GraphDB')
for s, p, o in g:
    if 'BNode' in str(type(s)):
        g.remove((s,None,None))
    if 'http://lexbib.org/agents/person' in str(s):
        g.remove((s,None,None))



g.serialize(destination=interimfile.replace('.rdf', '_upload.ttl'), format="turtle")

with open('D:/LexBib/journals/journals.json', 'w', encoding="utf-8") as outfile:
    json.dump(issndict, outfile, indent=2)
