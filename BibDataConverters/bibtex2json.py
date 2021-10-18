import json
import os
import sys
import bibtexparser
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# ask for file to process
print('Please select bibtex .bib file to be processed.')
Tk().withdraw()
infile = askopenfilename()
print('This file will be processed: '+infile)

if (os.path.isfile(infile) == False) or (infile.endswith('.bib') == False):
	print('Error opening file.')
	sys.exit()

print('Please wait while parsing bibtex...')
with open(infile, encoding="utf-8") as f:
	bibdata = bibtexparser.load(f)

print('File parsed. Please white while writing dump json file...')
result = []

for entry in bibdata.entries:
	result.append(entry)
	
with open(infile.replace(".bib",".json"), "w", encoding="utf-8") as f:
	json.dump(result, f)

print('\nFinished. Saved json file in the same folder.')
