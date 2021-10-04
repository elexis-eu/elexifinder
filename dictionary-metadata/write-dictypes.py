import lxml
from xml.etree import ElementTree
import re
import json
import time
import csv
import os
import sys
sys.path.insert(1, os.path.realpath(os.path.pardir))
from wikibase import lwb
from wikibase import config

with open('D:/LexBib/obelex-dict/dictypes_lwb.csv', 'r', encoding="utf-8") as csvfile:
	obelextypes = csv.DictReader(csvfile, delimiter="\t")
	obelextypenames = {}
	for type in obelextypes:
		lwbqid = type['lwb_qid']
		collstatement = lwb.updateclaim(lwbqid,"P74","Q16010",'item')
		lwb.setqualifier(lwbqid,"P74",collstatement,"P110",type['label'],"string")
