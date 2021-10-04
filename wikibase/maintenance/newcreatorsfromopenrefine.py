import csv
import json
import re
import time
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import os
import sys
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb


# This expects a csv with the following colums:
# bibItem [bibitem lwb Qid] / creatorstatement / listpos / fullName / Qid [reconciled person item lwb-qid] / givenName / lastName

# ask for file to process
print('Please select Zotero export JSON to be processed.')
Tk().withdraw()
infile = askopenfilename()
print('This file will be processed: '+infile)

if (os.path.isfile(infile) == False) or (infile.endswith('.csv') == False):
	print('Error opening file.')
	sys.exit()

with open(infile, encoding="utf-8") as f:
	data = csv.DictReader(f)

	#statement_id_re = re.compile(r'statement\/(Q\d+)\-(.*)')
	count = 1
	newcreators = {}
	for item in data:
		print('\nItem ['+str(count)+']:')
		bibItem = item['bibItem'].replace("http://lexbib.elex.is/entity/","")
		print('BibItem is '+bibItem+'.')
		creatorstatement = re.search(r'statement/(Q.*)', item['creatorstatement']).group(1)
		print('CreatorStatement is '+creatorstatement+'.')
		if 'Qid' in item and item['Qid'].startswith("Q"): # write creator item to creatorstatement
			creatorqid = item['Qid']
			lwb.setclaimvalue(creatorstatement, creatorqid, "item")
			creatoritemlabel = lwb.getlabel(creatorqid,"en")
			creatoritemaliaslist = lwb.getaliases(creatorqid,"en")
			if (item['fullName'] != creatoritemlabel) and (item['fullName'] not in creatoritemaliaslist):
				print('This is a new name variant for '+creatorqid+': '+item['fullName'])
				lwb.setlabel(creatorqid,"en",item['fullName'],type="alias")
		else: # crate a new person item and write it to creatorstatement
			if item['FullName'] not in newcreators:
				print('Will create new person item for '+item['fullName'])
				creatorqid = lwb.newitemwithlabel("Q5","en",item['fullName'])
				lwb.stringclaim(creatorqid,"P101",item['givenName'])
				lwb.stringclaim(creatorqid,"P102",item['lastName'])
				lwb.setlabel(creatorqid,"en",item['lastName']+", "+item['givenName'], type="alias")
			else:
				print('A person item for this fullName has been created before in this iteration of the script and will be re-used: '+item['fullName'])
				creatorqid = newcreators[item['FullName']]
			lwb.setclaimvalue(creatorstatement, creatorqid, "item")
		count +=1
		time.sleep(1)
