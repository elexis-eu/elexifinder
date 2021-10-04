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

corpname = "LexBib Oct 2021 stopterms"

# ask for file to process
print('Please select termstats JSON to be processed.')
Tk().withdraw()
infile = askopenfilename()
print('This file will be processed: '+infile)
try:
	with open(infile, encoding="utf-8") as f:
		data =  json.load(f)
		data_length = len(data)
except Exception as ex:
	print ('Error: file does not exist.')
	print (str(ex))
	sys.exit()

count = 0
for termqid in data:
	count += 1
	print('\nNow processing '+str(count)+' ('+termqid+'), '+str(data_length-count)+' items left.')
	existingstatements = lwb.getclaims(termqid,"P109")[1]
	#print('existingcreators: '+str(existingcreators))
	skip = False
	if existingstatements and ("P109" in existingstatements):
		for existingstatement in existingstatements["P109"]:
			if "qualifiers" in existingstatement and "P84" in existingstatement['qualifiers']:
				for sourceclaim in existingstatement['qualifiers']["P84"]:
					if sourceclaim['datavalue']['value'] == corpname:
						print('Found redundant source claim, skipped.')
						skip = True
	if not skip:
		hits_statement = lwb.updateclaim(termqid,"P109",str(data[termqid]),"string")
		lwb.setqualifier(termqid, "P109", hits_statement, "P84", corpname, "string")
