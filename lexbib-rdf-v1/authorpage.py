

import re
import json
import os
from datetime import datetime
import shutil
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import sys
from rdflib import Graph, Namespace, BNode, URIRef, Literal
import time
from csv import reader

aupubs = {}
with open('D:/LexBib/persons/person_pubs.csv', 'r', encoding="utf-8") as pubcsvfile: # source file
    aupubcsv = reader(pubcsvfile, delimiter=",")
    aupubheader = next(aupubcsv)
    sortaupubcsv = sorted(aupubcsv, key=lambda row: row[3])
    for row in sortaupubcsv:
        au = row.pop(0)
        if au not in aupubs:
            aupubs[au] = []
        aupubs[au].append(row)
    #print(aupubs)

aulocs = {}
with open('D:/LexBib/persons/person_locs.csv', 'r', encoding="utf-8") as loccsvfile: # source file
    auloccsv = reader(loccsvfile, delimiter=",")
    aulocheader = next(auloccsv)
    sortauloccsv = sorted(auloccsv, key=lambda row: row[5])

    for row in sortauloccsv:
        puburi = row.pop(0)
        #print(puburi)
        aut = row.pop(0)
        #print(aut)
        if aut not in aulocs:
            aulocs[aut] = []
        aulocs[aut].append(row)
        #print(aulocs[aut])
    #print(aulocs)

aucos = {}
with open('D:/LexBib/persons/person_coauthors.csv', 'r', encoding="utf-8") as cocsvfile: # source file
    aucocsv = reader(cocsvfile, delimiter=",")
    aucoheader = next(aucocsv)
    sortaucocsv = sorted(aucocsv, key=lambda row: row[1])
    for row in sortaucocsv:
        aut = row.pop(0)
        if aut not in aucos:
            aucos[aut] = []
        aucos[aut].append(row)

g = Graph()

gn = Namespace('http://www.geonames.org/ontology#')
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
dcterms = Namespace ('http://purl.org/dc/terms/')
wd = Namespace ('http://www.wikidata.org/entity/')
foaf = Namespace ('http://xmlns.com/foaf/0.1/')
skosxl = Namespace('http://www.w3.org/2008/05/skos-xl#')
lexdo = Namespace('http://lexbib.org/lexdo/')
lexperson = Namespace('http://lexbib.org/agents/person/')

g.bind("gn", gn)
g.bind("skos", skos)
g.bind("rdf", rdf)
g.bind("dcterms", dcterms)
g.bind("wd", wd)
g.bind("foaf", foaf)
g.bind("skosxl", skosxl)
g.bind("lexdo", lexdo)
g.bind("lexperson", lexperson)

g.parse('D:/LexBib/persons/lexpersons.ttl', format="ttl")

authorlist = g.subjects(predicate=rdf.type, object=lexdo.Person)
for authoruri in authorlist:

    author = re.search('(http://lexbib.org/agents/person/)(.*)', authoruri)
    if not os.path.exists('D:/LexBib/persons/pages/'+author[2]):
        os.makedirs('D:/LexBib/persons/pages/'+author[2])
    authorfilename = 'D:/LexBib/persons/pages/'+author[2]+'/index.html'
    with open(authorfilename, 'w', encoding="utf-8") as authorfile:
        authorfile.write('<html><head><meta charset="UTF-8"></head>\n<h1>LexBib author <i>'+author[2]+'</i> profile page, test version</h1>\n')
        authorfile.write('<p>Author URI is <a href="'+str(authoruri)+'">'+str(authoruri)+'</a>.')
        authorfile.write('<h2>Most frequent name variant</h2>\n')
        preflabellist = g.objects(subject=authoruri, predicate=skosxl.prefLabel)
        for label in preflabellist:
            #print(label)
            litformvals = g.objects(subject=label, predicate=skosxl.literalForm)
            for val in litformvals:
                authorfile.write('<p>Complete Name: <b>'+str(val)+'</b><p>\n')
            firstnamevals = g.objects(subject=label, predicate=foaf.firstName)
            for val in firstnamevals:
                authorfile.write('<p>First Name: <b>'+str(val)+'</b></p>\n')
            surnamevals = g.objects(subject=label, predicate=foaf.surname)
            for val in surnamevals:
                authorfile.write('<p>Last Name: <b>'+str(val)+'</b></p>\n')

        altlabellist = g.objects(subject=authoruri, predicate=skosxl.altLabel)
        for label in altlabellist:
            authorfile.write('<h2>Less frequent name variant</h2>\n')
            litformvals = g.objects(subject=label, predicate=skosxl.literalForm)
            for val in litformvals:
                authorfile.write('<p>Complete Name: <b>'+str(val)+'</b><p>\n')
            firstnamevals = g.objects(subject=label, predicate=foaf.firstName)
            for val in firstnamevals:
                authorfile.write('<p>First Name: <b>'+str(val)+'</b></p>\n')
            surnamevals = g.objects(subject=label, predicate=foaf.surname)
            for val in surnamevals:
                authorfile.write('<p>Last Name: <b>'+str(val)+'</b></p>\n')

        authorfile.write('<h2>Publications in LexBib</h2>\n<table>')
        #print (authoruri)
        if str(authoruri) in aupubs:
            #print('found author!')
            for pub in aupubs[str(authoruri)]:
                #print(pub)
                bibitem = pub[0]
                zotitem = pub[1]
                year = pub[2]
                title = pub[3]
                contst = pub[4]
                authorfile.write('<tr><td>'+contst+': </td><td><a href="'+zotitem+'">'+title+'</a></td></tr>')
        authorfile.write('</table>\n')
        authorfile.write('<h2>Locations in LexBib</h2>\n<table>')
        #print (authoruri)
        if str(authoruri) in aulocs:
            #print('found author!')
            for loc in aulocs[str(authoruri)]:
                #print(pub)
                wdloc = loc[0]
                loclabel = loc[1]
                countrylabel = loc[2]
                year = loc[3]
                authorfile.write('<tr><td>'+year+': </td><td><a href="'+wdloc+'">'+loclabel+', '+countrylabel+'</a></td></tr>')
        authorfile.write('</table>\n')
        authorfile.write('<h2>Co-authors in LexBib</h2>\n<p>')
        #print (authoruri)
        if str(authoruri) in aucos:
            #print('found author!')
            seen = []
            for co in aucos[str(authoruri)]:
                if co not in seen:
                    coaut = co[0]
                    colabel = co[1]
                    authorfile.write('<a href="'+coaut+'">'+colabel+'</a>   ')
                    seen.append(co)
        authorfile.write('</p>\n')

        authorfile.write('<p>This page was created by team [ AT ] lexbib [ DOT] org, based on data present in LexBib RDF database on '+str(datetime.now())[0:10]+' (see actual <a href="http://lexbib.org/blog/elexifinder-lexbib-collection-status/">status</a>.)</p>\n')
        authorfile.write('</html>')

print ('Begin building author index page...')

with open('D:/LexBib/persons/authorindex/authorindex-stub-begin.html', 'r', encoding="utf-8") as stubbeginfile:
    stubbegin = stubbeginfile.read().replace('\n', '')
with open('D:/LexBib/persons/authorindex/authorindex-stub-end.html', 'r', encoding="utf-8") as stubendfile:
    stubend = stubendfile.read().replace('\n', '')
with open('D:/LexBib/persons/lexpersons.csv', 'r', encoding="utf-8") as csvfile:
    aucsv = reader(csvfile, delimiter="\t")
    aucsvheader = next(aucsv)
    sortedaucsv = sorted(aucsv, key=lambda row: row[0])

    with open('D:/LexBib/persons/authorindex/index.html', 'w', encoding="utf-8") as indexfile:
        indexfile.write(stubbegin)
        indexfile.write('<table id="authortable">\n<tr class="header"><th style="width:20%;">URI / Page</th><th style="width:30%;">Full Name</th><th style="width:20%;">First Name</th><th style="width:20%;">Last Name</th><th style="width:10%;">Frequency</th></tr>\n')
        for row in sortedaucsv:
            authoruri = '<a href="'+row[0]+'">'+row[0].replace('http://lexbib.org/agents/person/', '')+'</a>'
            namelabel = row[1]
            firstname = row[2]
            lastname = row[3]
            frequence = row[4]

            if len(authoruri) > 1:
                indexfile.write('<tr>')
                indexfile.write('<td>%s</td>' % authoruri)
                indexfile.write('<td>%s</td>' % namelabel)
                indexfile.write('<td>%s</td>' % firstname)
                indexfile.write('<td>%s</td>' % lastname)
                indexfile.write('<td>%s</td>' % frequence)
                indexfile.write('</tr>\n')
        indexfile.write('</table>\n')
        indexfile.write('<p>This table was created on '+str(datetime.now())[0:10]+' by team [ AT ] lexbib [ DOT] org</p>')
        indexfile.write(stubend)

print('Done.')
