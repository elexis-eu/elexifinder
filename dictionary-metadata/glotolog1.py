import json
import os
import sys
import re
#import bibtexparser
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
result = ""
print('Please wait while parsing bibtex...')
with open(infile, encoding="utf-8") as f:
	bibdata = f.read().split('\n}')
	for item in bibdata:
		if 'hhtype' in item:
			hhtype = re.search(r'hhtype *= \{([^\}]+)\}',item).group(1)
			if 'dictionary' in hhtype:
				#result.append(item+"}\n\n")
				result += item+"}\n\n"


print('File parsed. Please white while writing dump json file...')
# result = []
#
# for entry in bibdata.entries:
# 	if "hhtype" in entry and "dictionary" in hhtype:
# 		result.append(entry)
# 		print('Found hhtype dictionary: '+item['ID'])

with open(infile.replace(".bib","_2.bib"), "w", encoding="utf-8") as f:
	f.write(result)

# with open(infile.replace(".bib","_2.json"), "w", encoding="utf-8") as f:
# 	json.dump(result, f)

print('\nFinished. Saved json file in the same folder.')
