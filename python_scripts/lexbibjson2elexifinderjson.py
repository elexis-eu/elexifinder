## treats output from LexBib RDF database (SPARQL query result as JSON, produced in VocBench3)

import re
import json
import os
from datetime import datetime

infile = "D:/LexBib/rdf2json/query-result.json" # path to LexBibRDF JSON SPARQL result

pubTime = str(datetime.fromtimestamp(os.path.getmtime(infile)))[0:22].replace(' ','T')
print(pubTime)

with open(infile, encoding="utf-8") as f:
	data =  json.load(f, encoding="utf-8")
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
		target['crawlTm'] = item['modTM']['value'].replace(' ', 'T')+'.00'
	if 'zotItemUri' in item:
		zotItemUri = item['zotItemUri']['value']    #+'?usenewlibrary=0'
		target['details'] = {"zotItemUri":zotItemUri}
	#	if 'details' not in target:
	#		target['details'] = []
	#	target['details'].append({'zotItemUri':zotItemUri})
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
		print("\nFound cleaned full text path at "+txtfile+" for "+target['uri'])
		txtfilecount = txtfilecount + 1
	elif 'pdffile' in item:
		#textname = re.match(r'/[A-Z0-9]+/[^\.]+\.pdf', item['pdffile']['value']).group(0).replace('.pdf','_body.txt')
		grobidbody =  re.match(r'([^\.]+)\.pdf', item['pdffile']['value']).group(1).replace('D:/Zotero/storage/', 'D:/LexBib/exports/exported_files/')+'_body.txt'
		print(grobidbody)
		if os.path.exists(grobidbody):
			txtfile = grobidbody
			print("\nFound GROBID processed full text body at "+txtfile+" for "+target['uri'])
			grobidcount = grobidcount + 1
	elif 'pdftxt' in item:
		txtfile = item['pdftxt']['value']
		print("\nFound pdf2txt full text path at "+txtfile+" for "+target['uri'])
		pdftxtcount = pdftxtcount + 1
	if txtfile != "":
		try:
			with open(txtfile, 'r', encoding="utf-8", errors="ignore") as file:
				fulltxt = file.read().replace('\n', ' ')
				target['body'] = fulltxt
				#print("\nCaught full text from "+txtfile+" for "+target['uri'])
		except:
			print("\n File "+txtfile+" for "+target['uri']+" was supposed to be there but not found")
			pass


		elexifinder.append(target)


with open('D:/LexBib/rdf2json/processed.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(elexifinder, json_file, indent=2)
	print("\n=============================================\nCreated processed JSON file. Finished.\n\n"+str(txtfilecount)+" files from manual attachments, "+str(grobidcount)+" files from GROBID output, "+str(pdftxtcount)+" files from Zotero pdf2txt")
