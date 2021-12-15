## produces dataset for ingestion by Event Registry software (http://finder.elex.is installation)

import re
import json
import os
import csv
import time
from datetime import datetime
import shutil
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import sys
import sparql

# items to export

export_items = """Q9054
Q13618
Q10752
Q13279
Q12734
Q8693
Q12270
Q11845
Q15742
Q11229
""".split("\n")

# pubTime
pubTime = str(datetime.now()).replace(' ','T')[0:22]
print(pubTime)

# get donelist
with open('D:/LexBib/elexifinder/export_last_donelist.txt', 'r', encoding="utf-8") as txt_file:
	donelist = txt_file.read().split("\n")

def get_item_data(itemuri):
	query = """
	PREFIX lwb: <http://lexbib.elex.is/entity/>
PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
PREFIX lp: <http://lexbib.elex.is/prop/>
PREFIX lps: <http://lexbib.elex.is/prop/statement/>
PREFIX lpq: <http://lexbib.elex.is/prop/qualifier/>
PREFIX lpr: <http://lexbib.elex.is/prop/reference/>
PREFIX lno: <http://lexbib.elex.is/prop/novalue/>

SELECT
?bibItem
(CONCAT('[ ',GROUP_CONCAT(?authordata; separator=", "),' ]') AS ?authorsJson)
?collection
?title
?articleTM
(sample(?zotItem) as ?zotItemUri)
?publang
#(group_concat(distinct strafter(str(?pdffile),"http://lexbib.org/zotero/");separator="@") as ?pdffiles)
#(group_concat(distinct strafter(str(?txtfile),"http://lexbib.org/zotero/");separator="@") as ?txtfiles)
(sample(?fullTextUrls) as ?fullTextUrl)
(sample(?containerFullTextUrl) as ?containerUrl)
#(sample(?containerUrl) as ?containerUrl)
(sample(?containerShortTitle) as ?containerShortTitle)
?authorLoc
?articleLoc
?articleLocLabel
?articleCountryLabel
(sample(strafter(str(?p100),"http://lexbib.elex.is/entity/")) as ?bibitemtype)

where {
  BIND(lwb:"""+itemuri+""" as ?bibItem)
  ?bibItem lp:P12 ?authorstatement .
  ?authorstatement lps:P12 ?authornode .
  ?authorstatement lpq:P33 ?listpos .
  ?authornode rdfs:label ?authorlabel .
 BIND ( concat ('{"uri": "', strafter(str(?authornode),"http://lexbib.elex.is/entity/"),
                '", "name": "', ?authorlabel, '", "listpos": "', ?listpos, '"}') as ?authordata )
  ?bibItem ldp:P5 lwb:Q3 .
  ?bibItem ldp:P85 ?collection .
  ?bibItem ldp:P6 ?title .
  ?bibItem ldp:P100 ?p100 . # ?p100 rdfs:label ?p100label . filter(lang(?p100label)="en")
  ?bibItem ldp:P15 ?articleTM .
  ?bibItem ldp:P11 ?langItem . ?langItem ldp:P32 ?publang .
  ?bibItem lp:P16 ?zotstatement.
  ?zotstatement lps:P16 ?zotItem.
#  OPTIONAL {?zotstatement lpq:P70 ?pdffile .}
#  OPTIONAL {?zotstatement lpq:P71 ?txtfile .}
  OPTIONAL {?bibItem ldp:P21|ldp:P44 ?fullTextUrls .}
  OPTIONAL {?bibItem ldp:P29 ?auLocUri . ?auLocUri ldp:P66 ?authorLoc .}
  OPTIONAL {?bibItem ldp:P9 ?containerUri .
  OPTIONAL {?containerUri ldp:P21|ldp:P111 ?containerFullTextUrl .}
  OPTIONAL {?containerUri ldp:P97 ?containerShortTitle .}
  OPTIONAL {?bibItem ldp:P36 ?event. ?event ldp:P50 ?eventloc.
            ?eventloc ldp:P66 ?articleLoc; rdfs:label ?articleLocLabel . filter(lang(?articleLocLabel)="en")
            ?eventloc ldp:P65 ?articleCountry. ?articleCountry rdfs:label ?articleCountryLabel. filter(lang(?articleCountryLabel)="en") }


}
}GROUP BY
 ?bibItem
 ?authorsJson
 ?collection
 ?title
 ?articleTM
 ?zotItemUri
 ?publang
# ?pdffiles
# ?txtfiles
 ?fullTextUrl
 ?containerUrl
 #?containerUrl
 ?containerShortTitle
 ?authorLoc
 ?articleLoc
 ?articleLocLabel
 ?articleCountryLabel
 ?bibitemtype
limit 10
	"""
	url = "https://lexbib.elex.is/query/sparql"
	print("Waiting for SPARQL to deliver item data...")
	sparqlresults = sparql.query(url,query)
	for row in sparqlresults:
		itemdata = sparql.unpack_row(row, convert=None, convert_type={})
		#print(str(itemdata))
		print('Got item data.')
		return itemdata


# collection images links:

images = {
1 : "https://elex.is/wp-content/uploads/2020/12/collection_1_elex.jpg.",
2 : "https://elex.is/wp-content/uploads/2020/12/collection_2_euralex.jpg",
3 : "https://elex.is/wp-content/uploads/2020/12/collection_3_ijl.jpg",
4 : "https://elex.is/wp-content/uploads/2020/12/collection_4_lexikos.jpg",
5 : "https://elex.is/wp-content/uploads/2020/12/collection_5_lexiconordica.jpg",
6 : "https://elex.is/wp-content/uploads/2020/12/collection_6_lexicographica.jpg",
7 : "https://elex.is/wp-content/uploads/2020/12/collection_7_NSL.jpg",
8 : "https://elex.is/wp-content/uploads/2020/12/collection_8_lexicon_tokyo.jpg",
9 : "https://elex.is/wp-content/uploads/2020/12/collection_9_lexicography_asialex.jpg",
10 : "https://elex.is/wp-content/uploads/2020/12/collection_10_globalex.jpg",
11 : "https://elex.is/wp-content/uploads/2020/12/collection_11_videolectures.jpg",
12 : "https://elex.is/wp-content/uploads/2020/12/collection_12_dsna.jpg",
13 : "https://elex.is/wp-content/uploads/2020/12/collection_13_teubert.jpg",
14 : "https://elex.is/wp-content/uploads/2020/12/collection_14_fuertesolivera.jpg",
15 : "https://elex.is/wp-content/uploads/2020/12/collection_15_mullerspitzer.jpg",
16 : "https://elex.is/wp-content/uploads/2020/12/collection_16_slovenscina.jpg",
17 : "https://elex.is/wp-content/uploads/2020/12/collection_17_rdelexicografia.jpg"
}

# load subject list
with open('D:/LexBib/terms/elexifinder-catlabels.csv', encoding="utf-8") as csvfile:
	catlabels_csv = csv.DictReader(csvfile)
	catlabels = {}
	for row in catlabels_csv:
		termqid = row['term'].replace("http://lexbib.elex.is/entity/","")
		#erlabel = re.search(r'[\w ]+$',row['ercat']).group(0)
		catlabels[termqid] = {"uri":row['ercat'].replace(" ","_"),"label":row['ercat'].replace("Lexicography/","")}

#print(str(catlabels))

with open('D:/LexBib/bodytxt/foundterms.json', encoding="utf-8") as jsonfile:
	foundterms = json.load(jsonfile)

with open('D:/LexBib/bodytxt/bodytxt_collection.json', encoding="utf-8") as jsonfile:
	bodytxts = json.load(jsonfile)

# Tk().withdraw()
# infile = askopenfilename()
# print('This file will be processed: '+infile)
#
# try:
#     version = int(re.search('_v([0-9])', infile).group(1))
# except:
#     print('No version number in file name... Which version is this? Type the number.')
#     try:
#         version = int(input())
#     except:
#         print ('Error: This has to be a number.')
#         sys.exit()
#     pass
#
# pubTime = str(datetime.fromtimestamp(os.path.getmtime(infile)))[0:22].replace(' ','T')
# print(pubTime)
# try:
#     with open(infile, encoding="utf-8") as f:
#         data =  json.load(f, encoding="utf-8")
# except:
#     print ('Error: file does not exist.')
#     sys.exit()
#
# results = data['results']
# bindings = results['bindings']
#print(bindings)
elexifinder = []
txtfilecount = 0
grobidcount = 0
pdftxtcount = 0
itemcount = 0
problemlog = []

for itemuri in export_items:

	if itemuri in donelist:
		print(itemuri+" is in donelist, skipped.")
		continue


	itemcount += 1
	target = {}
	target['uri'] = itemuri
	print('\n['+str(itemcount)+'] '+itemuri)

	# get term indexation
	target['categories'] = []
	if itemuri not in foundterms:
		print('No term indexation found for item '+itemuri)
		time.sleep(1)
	else:
		for foundterm in foundterms[itemuri]:
			if foundterm not in catlabels:
				print('er-catlabel not found. Must be a redirect uri.')
				time.sleep(1)
				continue
			if catlabels[foundterm] not in target['categories']:
				target['categories'].append(catlabels[foundterm])
				#print('Term found in this item: '+str(catlabels[foundterm]))

	# get item data
	itemdata = get_item_data(itemuri)

	target['pubTm'] = pubTime
	target['version'] = 3
	target['details'] = {'collection_version': 3}

	target['authors'] = json.loads(itemdata[1])
	target['title'] = itemdata[3]
	target['articleTm'] = str(itemdata[4])[0:22].replace(' ','T')

	# target['crawlTm'] = item['modTM']['value'][0:22]
	zotItemUri = "https://www.zotero.org/groups/1892855/lexbib/items/"+itemdata[5]+"/item-details"
	target['details']['zotItemUri'] = zotItemUri
	target['url'] = itemdata[8]
	collection = int(itemdata[2])
	target['details']['collection'] = collection
	if collection in images:
		target['images']=images[collection]
	else:
		target['images']="https://elex.is/wp-content/uploads/2021/03/elexis_logo_default.png"
#	if 'container' in item:
#		target['sourceUri'] = item['container']['value'] # replaced by containerFullTextUrl or containerUri
	# if 'containerFullTextUrl' in item:
	# 	target['sourceUri'] = item['containerFullTextUrl']['value']
	# 	target['url'] = item['containerFullTextUrl']['value'] # this overwrites zotero item in target['url']
	# elif 'containerUri' in item:
	# 	target['sourceUri'] = item['containerUri']['value']
	# 	target['url'] = item['containerUri']['value'] # this overwrites zotero item in target['url']
	# if 'sourceUri' not in target:
	# 	print ('*** ERROR: nothing to use as sourceUri in '+itemuri+'!')
	# 	problemlog.append('*** ERROR: nothing to use as sourceUri in '+itemuri+'!\n')
	target['sourceTitle'] = itemdata[9]

	target['lang'] = itemdata[6]
	if itemdata[11]:
		target['sourceLocUri'] = itemdata[11]
		target['sourceLocP'] = True
	else:
		target['sourceLocP'] = False
	if itemdata[12]:
		target['sourceCity'] = itemdata[12] # item['articleLocLabel']['value']
	if itemdata[13]:
		target['sourceCountry'] = itemdata[13] # item['articleCountryLabel']['value']
	if itemdata[10]:
		target['locationUri'] = itemdata[10]  # item['authorLoc']['value']
	if itemdata[7]: # this overwrites zotero item URL in target['url']
		target['url'] = itemdata[7] # item['fullTextUrl']['value']
	if itemdata[14] == "Q30":
		target['type'] = "video"
	else:
		target['type'] = "news" # item type for all except videos
	if itemuri in bodytxts:
		target['body'] = bodytxts[itemuri]['bodytxt']
		print('Textbody found and copied.')
	else:
		print('No textbody found.')

#write to JSON
	elexifinder.append(target)
	with open('D:/LexBib/elexifinder/export_last.jsonl', 'a', encoding="utf-8") as jsonl_file:
		jsonl_file.write(json.dumps(target)+'\n')
	donelist.append(itemuri)
	with open('D:/LexBib/elexifinder/export_last_donelist.txt', 'a', encoding="utf-8") as txt_file:
		txt_file.write(itemuri+'\n')

# end of item loop

# with open(infile.replace('.json', '_problemlog.json'), 'w', encoding="utf-8") as problemfile:
# 	problemfile.write(str(problemlog))

elexidict = {}
for item in elexifinder:
	elexidict[item['uri']] = item

with open('D:/LexBib/elexifinder/export_last.json', 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(elexidict, json_file, indent=2)
	print("\n=============================================\nCreated processed JSON file.. Finished.\n")
