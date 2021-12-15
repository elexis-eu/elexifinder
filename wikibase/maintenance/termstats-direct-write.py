import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv
import re
import time
import json
from tkinter import Tk
from tkinter.filedialog import askopenfilename

corpname = "LexBib en/es 12-2021"

# ask for file to process
print('Please select termstats JSON to be processed.')
Tk().withdraw()
infile = askopenfilename()
print('This file will be processed: '+infile)
try:
	with open(infile, encoding="utf-8") as f:
		termstats =  json.load(f)
		data_length = len(termstats['all_langs'])
except Exception as ex:
	print ('Error: file does not exist.')
	print (str(ex))
	sys.exit()

count = 0
for termqid in termstats['all_langs']:
	count += 1
	print('\nNow processing '+str(count)+' ('+termqid+'), '+str(data_length-count)+' items left.')
	existingstatements = lwb.getclaims(termqid,"P109")[1]
	found_in_articles = str(termstats['all_langs'][termqid])
	p84quali = None
	hits_statement = None
	if existingstatements and ("P109" in existingstatements):
		for existingstatement in existingstatements["P109"]:
			if existingstatement['mainsnak']['datavalue']['value'] == found_in_articles:
				hits_statement = existingstatement['id']
				print('Found existing statement with that value.')
				# if "qualifiers" in existingstatement and "P84" in existingstatement['qualifiers']:
				# 	for sourceclaim in existingstatement['qualifiers']["P84"]:
				# 		if sourceclaim['datavalue']['value'] == corpname:
				# 			print('Found redundant p84 quali, skipped.')
				# 			p84quali = True
				break
	if not hits_statement:
		hits_statement = lwb.stringclaim(termqid,"P109",found_in_articles)
	if not p84quali:
		lwb.setqualifier(termqid, "P109", hits_statement, "P84", corpname, "string")
