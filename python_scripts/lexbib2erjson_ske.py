## treats output from LexBib RDF database (SPARQL query result as JSON, produced in VocBench3)

import re
import json
import os
import csv
from datetime import datetime
import shutil
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import sys
import requests
import time

#set up SkE
with open('D:/LexBib/SkE/pwd.txt', 'r', encoding='utf-8') as pwdfile:
	pwd = pwdfile.read()

ske_auth = ('jsi_api', pwd)
print(ske_auth)
ske_url = 'https://api.sketchengine.eu/ca/api'

with open('D:/LexBib/SkE/ske_dict.json', 'r', encoding='utf-8') as skelogfile:
	ske_log = json.load(skelogfile)
	print("ske_log:\n"+str(ske_log)+"\n")


isodict = {}
with open('D:/LexBib/languages/lexvo-iso639-1.tsv', 'r', encoding="utf-8") as isofile:
	rows = csv.reader(isofile, delimiter='\t')
	for row in rows:
		isodict[row[1].replace('http://lexvo.org/id/iso639-3/','')] = row[0]


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
# 12 : "https://elex.is/wp-content/uploads/2020/12/collection_12_dsna.jpg",
13 : "https://elex.is/wp-content/uploads/2020/12/collection_13_teubert.jpg",
14 : "https://elex.is/wp-content/uploads/2020/12/collection_14_fuertesolivera.jpg",
15 : "https://elex.is/wp-content/uploads/2020/12/collection_15_mullerspitzer.jpg",
16 : "https://elex.is/wp-content/uploads/2020/12/collection_16_slovenscina.jpg",
17 : "https://elex.is/wp-content/uploads/2020/12/collection_17_rdelexicografia.jpg"
}


with open('D:/LexBib/abstracts/abstracts.json', 'r', encoding="utf-8") as infile:
	absdict = json.load(infile, encoding="utf-8")



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
#print(bindings)
elexifinder = []
txtfilecount = 0
grobidcount = 0
pdftxtcount = 0
itemcount = 0
useduri = []
problemlog = []

for item in bindings:
	try:
		itemuri = item['uri']['value']
		if itemuri not in useduri:
			itemcount += 1
			target = {}
			target['uri'] = itemuri
			print('\n['+str(itemcount)+', '+str(len(bindings)-itemcount)+' left]\n'+itemuri)
			useduri.append(itemuri)

			target['pubTm'] = pubTime
			target['version'] = version
			target['details'] = {'collection_version':version}

			if 'authorsJson' in item:
				authorsJson = item['authorsJson']
				authorsliteral = authorsJson['value']
				target['authors'] = json.loads(authorsliteral)
			if 'title' in item:
				target['title'] = item['title']['value']
			else:
				print ('*** ERROR: mandatory key title not in '+itemuri+'!')
				problemlog.append('*** ERROR: mandatory key title not in '+itemuri+'!\n')
			if 'articleTM' in item:
				target['articleTm'] = item['articleTM']['value'][0:22]
				articleYear = item['articleTM']['value'][0:4]
			else:
				print ('*** ERROR: mandatory key articleTM not in '+itemuri+'!')
				problemlog.append('*** ERROR: mandatory key articleTM not in '+itemuri+'!\n')
			if 'modTM' in item:
				target['crawlTm'] = item['modTM']['value'][0:22]
			if 'zotItemUri' in item:
				zotItemUri = item['zotItemUri']['value'].replace("http://zotero.org/groups/1892855/items/","http://lexbib.org/zotero/")	#+'?usenewlibrary=0'
				target['details']['zotItemUri']=zotItemUri
				target['url'] = zotItemUri
			else:
				print ('*** ERROR: mandatory key zotItemUri not in '+itemuri+'!')
				problemlog.append('*** ERROR: mandatory key zotItemUri not in '+itemuri+'!\n')
				zotItemUri = "Error_UnknownZoteroID"
			if 'collection' in item:
				collection = int(item['collection']['value'])
				target['details']['collection']=collection
				if collection in images:
					target['images']=images[collection]
				else:
					target['images']="https://elex.is/wp-content/uploads/2021/03/elexis_logo_default.png"
			else:
				collection = 0
				target['images']="https://elex.is/wp-content/uploads/2021/03/elexis_logo_default.png"
		#	if 'container' in item:
		#		target['sourceUri'] = item['container']['value'] # replaced by containerFullTextUrl or containerUri
			if 'containerFullTextUrl' in item:
				target['sourceUri'] = item['containerFullTextUrl']['value']
				target['url'] = item['containerFullTextUrl']['value'] # this overwrites zotero item in target['url']
			elif 'containerUri' in item:
				target['sourceUri'] = item['containerUri']['value']
				target['url'] = item['containerUri']['value'] # this overwrites zotero item in target['url']
			if 'sourceUri' not in target:
				print ('*** ERROR: nothing to use as sourceUri in '+itemuri+'!')
				problemlog.append('*** ERROR: nothing to use as sourceUri in '+itemuri+'!\n')
			if 'containerShortTitle' in item:
				target['sourceTitle'] = item['containerShortTitle']['value']
			else:
				print ('*** ERROR: mandatory key containerShortTitle not in '+itemuri+'!')
				problemlog.append('*** ERROR: mandatory key containerShortTitle not in '+itemuri+'!\n')
			if 'publang' in item:
				target['lang'] = item['publang']['value']#[-3:]
			else:
				target['lang'] = ""
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
			if 'fullTextUrl' in item: # this overwrites zotero item URL in target['url']
				target['url'] = item['fullTextUrl']['value']

			if 'ertype' in item:
				target['type'] = item['ertype'] # not implemented yet; default is "news", if "videolectures" in "fullTextUrl", then "video"
			else:
				target['type'] = "news" # default event registry type
				if 'fullTextUrl' in item:
					if "videolectures" in item['fullTextUrl']['value']:
						target['type'] = "video"

			# load txt. Try (1), txt file manually attached to Zotero item, (2) GROBID body TXT, (3) pdf2txt
			txtfile = ""
			fulltextsource = "missing"
			grobidbody = ""
			pdffullpath = ""
			if 'txtfile' in item:
				txtfile = item['txtfile']['value']
				print("Found manually attached "+txtfile)
				fulltextsource = "manual_txt"
				txtfilecount = txtfilecount + 1
			if txtfile == "" and 'pdffile' in item:
				pdffullpath = item['pdffile']['value']

			try: # try if grobidbody is there
				pdffoldname = re.match('D:/Zotero/storage/([^\.]+)\.pdf', pdffullpath).group(1)
				grobidbodyfile = 'D:/LexBib/exports/export_filerepo/'+pdffoldname+'_body.txt'
				if os.path.exists(grobidbodyfile):
					txtfile = grobidbodyfile
					fulltextsource = "grobid"
					copyfilepath = 'D:/Zotero/storage/'
					shutil.copy('D:/LexBib/exports/export_filerepo/'+pdffoldname+'.tei.xml', copyfilepath+pdffoldname+'.tei.xml')
					shutil.copy('D:/LexBib/exports/export_filerepo/'+pdffoldname+'_body.txt', copyfilepath+pdffoldname+'_body.txt')
					print("Found GROBID processed full text body at "+txtfile)
					grobidcount = grobidcount + 1
			except:
				if txtfile == "" and pdffullpath == "":
					pdffoldname = "NO PDF ATTACHMENT FOLDER"
					print('\n...could not find GROBID _body.txt in folder '+pdffoldname+' (Text '+txtfile)
					print('Something is strange with this item: '+target['title']+'\n')
					problemlog.append('{"'+itemuri+'", "no PDF found"}')
				pass
			if txtfile== "" and 'pdftxt' in item:
				txtfile = item['pdftxt']['value']
				fulltextsource = "pdf2txt"
				print("Found .zotero-fulltext-cache path at "+txtfile)
				pdftxtcount = pdftxtcount + 1
			if txtfile != "":
				try:
					with open(txtfile, 'r', encoding="utf-8", errors="ignore") as file:
						bodytxt = file.read().replace('\n', ' ')

						#print("\nCaught full text from "+txtfile+" for "+target['uri'])
				except:
					print("File "+txtfile+" for "+target['uri']+" was supposed to be there but not found")
					txtfile = ""
					pass
			if txtfile == "":
				bodytxt = ""
				# last resort: an english abstract
				if itemuri in absdict and absdict[itemuri]['lang'] == "eng":
					bodytxt = absdict[itemuri]['text']
					fulltextsource = "abstract"
				else:
					if 'title' in item:
						bodytxt = item['title']['value']
						fulltextsource = "title"

			if fulltextsource != "":
				target['details']['bodytxtsource'] = fulltextsource
				target['body'] = bodytxt
			else:
				target['body'] = ""
				problemlog.append("*** PROBLEM: Nothing to use for target_body for "+itemuri)
				fulltextsource = "Error_no_text"

			if target['lang'] !="":
				iso6393 = target['lang']
			else:
				iso6393 = "eng"
				print('*** ERROR: Item has no pubLang. Set to English.')
				problemlog.append("*** PROBLEM: No PubLang for "+itemuri)
			iso6391 = isodict[iso6393]
			print('Publication language is '+iso6391+' ('+iso6393+').')
			corpname = "LexBib/Elexifinder v"+str(version)+" "+iso6393

			print('Corpus for this item will be '+corpname+'.')

			# send to SkE if not sent there before (look that up in ske_log.json)
			ske_docname = zotItemUri.replace('http://zotero.org/groups/1892855/items/',"")+"_coll"+str(collection)+"_"+articleYear+"_"+fulltextsource

			if corpname in ske_log and ske_docname in ske_log[corpname]['docs']:
				print('Item ['+str(itemcount)+'] is already present at SkE (Corpus name '+corpname+'), skipped.')
				#time.sleep(1)
			else:
				if corpname not in ske_log:

					while True:
						try:
							r = requests.post(ske_url + '/corpora', auth=ske_auth, json={
								'language_id': iso6391,
								'name': corpname
							})
							if "201" in str(r):
								print('Corpus '+corpname+' created.')
								break
							elif "400" in str(r): # this happens when language is unknown to SkE
								print('Language unknown to SkE. Item skipped.')
								problemlog.append('*** UNKNOWN LANGUAGE '+iso6391+'('+iso6393+') in item '+itemuri+' '+item['title']['value'])
								break
							else:
								print(str(r))
							time.sleep(1)
						except Exception as ex:
							print(str(ex))
							problemlog.append('*** PROBLEM: Error at corpus creation for '+itemuri+', language: '+iso6393+' ('+iso6391+') '+str(ex))
							pass

					corpus_id = r.json()['data']['id']
					corpus_url = ske_url + '/corpora/' + str(corpus_id)
					ske_log[corpname] = {'created':str(datetime.now())[0:19],'corpname':corpname,'corpus_url':corpus_url,'corpus_id':corpus_id,'language':iso6393,'docs':[]}
					print('Corpus ID: '+str(corpus_id)+'\nCorpus URL: '+corpus_url)
				else:
					corpus_id = ske_log[corpname]["corpus_id"]
					corpus_url = ske_log[corpname]["corpus_url"]

				ske_file = {'file': (ske_docname, bodytxt, 'text/plain')}
				while True:
					r = requests.post(corpus_url + '/documents', auth=ske_auth, files=ske_file, params={'feeling': 'lucky'})
					if "201" in str(r):
						print('File uploaded to corpus with ID ['+str(corpus_id)+']: '+ske_docname)
						break
					else:
						print(str(r))
						time.sleep(2)

				# while True:
				# 	print('Waiting for OK from SkE that new text is included...')
				#
				# 	r = requests.post(corpus_url + '/can_be_compiled', json={}, auth=ske_auth)
				# 	if r.json()['result']['can_be_compiled']:
				# 		break
				# 	time.sleep(1)

				# while True:
				# 	r = requests.post(corpus_url + '/compile', json={'structures': 'all'}, auth=ske_auth)
				# 	if "200" in str(r):
				# 		print('Corpus compilation successfully triggered.')
				# 		break
				# 	time.sleep(1)

				ske_log[corpname]["docs"].append(ske_docname)
				with open('D:/LexBib/SkE/ske_dict.json', 'w', encoding="utf-8") as skelogfile:
					json.dump(ske_log, skelogfile, indent=2)
				print ('Total success for item ['+str(itemcount)+'].')


		#write to JSON
			elexifinder.append(target)

		# if uri appears twice:
		else:
			print('\nItem '+itemuri+' is a duplicate, something is wrong with it, probably multiple attachments\n')
			problemlog.append('{"'+itemuri+'", "duplicate, probably multiple attachments"}')

		#time.sleep(5)
	except Exception as ex:
		problemlog.append('*** PROBLEM: Error at corpus creation for '+itemuri+': '+str(ex))
		print(str(ex))
		time.sleep(5)
		pass
	#time.sleep(0.5)
# end of item loop

with open(infile.replace('.json', '_problemlog.json'), 'w', encoding="utf-8") as problemfile:
	problemfile.write(str(problemlog))

elexidict = {}
with open(infile.replace('.json', '_EF.jsonl'), 'w', encoding="utf-8") as jsonl_file: # path to result JSONL file
	for item in elexifinder:
		jsonl_file.write(json.dumps(item)+'\n')
		elexidict[item['uri']] = item
	print("\n=============================================\nCreated processed JSONL file for "+infile+".")

with open(infile.replace('.json', '_EFdict.json'), 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(elexidict, json_file, indent=2)
	print("\n=============================================\nCreated processed JSON file for "+infile+". Finished.\n\n"+str(txtfilecount)+" files from manual attachments, "+str(grobidcount)+" files from GROBID output, "+str(pdftxtcount)+" files from Zotero pdf2txt")
