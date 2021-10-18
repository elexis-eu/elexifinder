import json
import os
import sys
#import bibtexparser
from tkinter import Tk
from tkinter.filedialog import askopenfilename

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
	bibdata = json.load(f)

print('File loaded. Please white while processing...')
result = {}

for item in bibdata:
	type = item['ENTRYTYPE']
	if type not in result:
		result[type] = [item]
	else:
		result[type].append(item)

with open(infile.replace(".json","_2.json"), "w", encoding="utf-8") as f:
	json.dump(result, f)

print('\nFinished. Saved json file in the same folder.')
