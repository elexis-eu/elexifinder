import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv
import json

with open(config.datafolder+'lexmeta/lexmeta_owl_upload.csv', 'r', encoding="utf-8") as csvfile:
	entities = csv.DictReader(csvfile)

	for entity in entities:
		lwbqid = entity['lwb']
		lexmeta_owl_entity = entity['lexmeta']
		lexmeta_owl_entity_class = entity['lexmeta_type']
		exact_match = entity['exact_match']
		statement = lwb.updateclaim(lwbqid,"P42",lexmeta_owl_entity,"url")
		lwb.setqualifier(lwbqid, "P42", statement, "P166", lexmeta_owl_entity_class, "url")
		if exact_match:
			lwb.setqualifier(lwbqid, "P42", statement, "P167", exact_match, "url")
		print('Done:',lwbqid,lexmeta_owl_entity,lexmeta_owl_entity_class,str(exact_match),"\n")
