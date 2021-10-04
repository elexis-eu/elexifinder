import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv
import json

timeobj = {'time':"+2021-08-21T00:00:00Z",'precision':11}

with open('D:/LexBib/lexonomy/stats/terms_in_Lexonomy.json', 'r', encoding="utf-8") as jsonfile:
	terms = json.load(jsonfile)

for term in terms:
	statement= lwb.updateclaim(term, "P117", timeobj, "time")
