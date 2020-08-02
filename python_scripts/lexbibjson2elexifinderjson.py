## treats output from LexBib RDF database (SPARQL query result as JSON, produced in VocBench3)

import re
import json
import os
from datetime import datetime
import shutil
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import sys

Tk().withdraw()
infile = askopenfilename()
print('This file will be processed: '+infile)

try:
    version = int(re.search('_v([0-9])', infile).group(1))
except:
    print('No version number in file name... Which version is this? Type the number.')
    try:
        version = int(input())
    except:
        print ('Error: This has to be a number.')
        sys.exit()
    pass

pubTime = str(datetime.fromtimestamp(os.path.getmtime(infile)))[0:22].replace(' ','T')
print(pubTime)
try:
    with open(infile, encoding="utf-8") as f:
        data =  json.load(f, encoding="utf-8")
except:
    print ('Error: file does not exist.')
    sys.exit()

results = data['results']
bindings = results['bindings']
print(bindings)
elexifinder = []
txtfilecount = 0
grobidcount = 0
pdftxtcount = 0

for item in bindings:
	target = {}
	target['pubTm'] = pubTime
	target['version'] = version
	target['details'] = [{'collection_version':version}]

	if 'authorsJson' in item:
		authorsJson = item['authorsJson']
		authorsliteral = authorsJson['value']
		target['authors'] = json.loads(authorsliteral)
	if 'uri' in item:
		target['uri'] = item['uri']['value']
	if 'title' in item:
		target['title'] = item['title']['value']
	if 'articleTM' in item:
		target['articleTm'] = item['articleTM']['value'][0:22]
	if 'modTM' in item:
		target['crawlTm'] = item['modTM']['value'][0:22]
	if 'zotItemUri' in item:
		zotItemUri = item['zotItemUri']['value']    #+'?usenewlibrary=0'
		target['details'].append({'zotItemUri':zotItemUri})
	if 'collection' in item:
		collection = int(item['collection']['value'])
		target['details'].append({'collection':collection})
	if 'container' in item:
		target['sourceUri'] = item['container']['value']
	if 'containerShortTitle' in item:
		target['sourceTitle'] = item['containerShortTitle']['value']
	if 'publang' in item:
		target['lang'] = item['publang']['value']#[-3:]
	if 'articleLoc' in item:
		target['sourceLocUri'] = item['articleLoc']['value']
		target['sourceLocP'] = True
	else:
		target['sourceLocP'] = False
	if 'articleLocLabel' in item:
		target['sourceCity'] = item['articleLocLabel']['value']
	if 'articleCountryLabel' in item:
		target['sourceCountry'] = item['articleCountryLabel']['value']
	if 'authorLoc' in item:
		target['locationUri'] = item['authorLoc']['value']
	if 'fullTextUrl' in item:
		target['url'] = item['fullTextUrl']['value']
	if 'ertype' in item:
		target['type'] = item['ertype']
	else:
		target['type'] = "news" # default event registry type
	# load txt. Try (1), txt file manually attached to Zotero item, (2) GROBID body TXT, (3) pdf2txt
	txtfile = ""
	grobidbody = ""
	if 'txtfile' in item:
		txtfile = item['txtfile']['value']
		print("\nFound manually attached "+txtfile+" for "+target['uri'])
		txtfilecount = txtfilecount + 1
	if txtfile == "" and 'pdffile' in item:
		pdffullpath = item['pdffile']['value']
	try:
		pdffoldname = re.match('D:/Zotero/storage/([^\.]+)\.pdf', pdffullpath).group(1)
		grobidbodyfile = 'D:/LexBib/exports/export_filerepo/'+pdffoldname+'_body.txt'
		if os.path.exists(grobidbodyfile):
			txtfile = grobidbodyfile
			copyfilepath = 'D:/Zotero/storage/'
			shutil.copy('D:/LexBib/exports/export_filerepo/'+pdffoldname+'.tei.xml', copyfilepath+pdffoldname+'.tei.xml')
			shutil.copy('D:/LexBib/exports/export_filerepo/'+pdffoldname+'_body.txt', copyfilepath+pdffoldname+'_body.txt')
			print("Found GROBID processed full text body at "+txtfile+" for "+target['uri'])
			grobidcount = grobidcount + 1
	except:
		pass
	if txtfile== "" and 'pdftxt' in item:
		txtfile = item['pdftxt']['value']
		print("\nFound pdf2txt full text path at "+txtfile+" for "+target['uri'])
		pdftxtcount = pdftxtcount + 1
	if txtfile != "":
		try:
			with open(txtfile, 'r', encoding="utf-8", errors="ignore") as file:
				bodytxt = file.read().replace('\n', ' ')
				target['body'] = bodytxt
				#print("\nCaught full text from "+txtfile+" for "+target['uri'])
		except:
			print("\n File "+txtfile+" for "+target['uri']+" was supposed to be there but not found")
			pass


		elexifinder.append(target)


with open(infile.replace('.json', '_EF.json'), 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(elexifinder, json_file, indent=2)
	print("\n=============================================\nCreated processed JSON file for "+infile+". Finished.\n\n"+str(txtfilecount)+" files from manual attachments, "+str(grobidcount)+" files from GROBID output, "+str(pdftxtcount)+" files from Zotero pdf2txt")
