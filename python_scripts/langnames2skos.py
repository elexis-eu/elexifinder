

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

with open('D:/LexBib/languages/langdict.json', encoding="utf-8") as f:
	langdict =  json.load(f, encoding="utf-8")


lexdo = Namespace('http://lexbib.org/lexdo/#')
rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
lexvo = Namespace ('http://lexvo.org/id/iso639-3/')
wd = Namespace ('http://www.wikidata.org/entity/')
lexdotop = Namespace ('http://lexbib.org/lexdo-top/')
lexterm = Namespace ('http://lexbib.org/terms#')

graph = Graph()
graph.bind("lexdo", lexdo)
graph.bind("skos", skos)
graph.bind("rdf", rdf)
graph.bind("lexvo", lexvo)
graph.bind("wd", wd)
graph.bind("lexdo-top", lexdotop)
graph.bind("lexterm", lexterm)

for isocode in langdict:

    langnode = URIRef(lexvo+isocode)
    rootterm = URIRef(lexterm+'Term_Language')
    scheme = URIRef(lexterm+'Scheme_Language')
    graph.add((langnode, rdf.type, skos.Concept))
    graph.add((langnode, skos.broader, rootterm))
    graph.add((langnode, skos.inScheme, scheme))

    for item in langdict[isocode]:
        langname = Literal(item['label'], lang=item['labelLang'])
        graph.add((langnode, skos.prefLabel, langname))



graph.serialize(destination="D:/LexBib/languages/language_skos.ttl", format="turtle")

print("Languages SKOS TTL file updated.")
