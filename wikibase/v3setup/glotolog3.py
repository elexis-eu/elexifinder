import json
import os
import sys
import re
#import bibtexparser
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import langmapping

# ask for file to process
print('Please select json file to be processed.')
Tk().withdraw()
infile = askopenfilename()
print('This file will be processed: '+infile)

if (os.path.isfile(infile) == False) or (infile.endswith('.json') == False):
	print('Error opening file.')
	sys.exit()

print('Please wait while parsing bibtex...')
with open(infile, encoding="utf-8") as f:
	bibdata = json.load(f)['book'] # books only

print('File loaded. Please white while processing...')
result = {}
missing_codes = []
for item in bibdata:

	glotId = item['ID']
	result[glotId] = {}


	if "lgcode" in item:
		result[glotId]['lgcodes'] = re.findall(r'\[\w{3}\]',item['lgcode'])
		lqid = []
		for code in result[glotId]['lgcodes']:
			qid = langmapping.getqidfromiso(code[1:3])
			if qid:
				lqid.append(qid)
			else:
				if code not in missing_codes:
					missing_codes.append(code)
		result[glotId]['lgqidlit'] = lqid

	if "inlg" in item:
		result[glotId]['inlgs'] = re.findall(r'\[\w{3}\]',item['inlg'])
		lqid = []
		for code in result[glotId]['inlgs']:
			qid = langmapping.getqidfromiso(code[1:3])
			if qid:
				lqid.append(qid)
			else:
				if code not in missing_codes:
					missing_codes.append(code)
		result[glotId]['inlgqidlist'] = lqid

	if "title" in item:
		result[glotId]['title'] = item['title']

	if "year" in item:
		result[glotId]['year'] = item['year']

	if "publisher" in item:
		result[glotId]['publisher'] = item['publisher']

	result[glotId]['itemdata'] = item

with open(infile.replace(".json","_2.json"), "w", encoding="utf-8") as f:
	json.dump(result, f)

with open(infile.replace(".json","_missingcodes.json"), "w", encoding="utf-8") as f:
	json.dump(missing_codes, f)

print('\nFinished. Saved json file in the same folder.')
