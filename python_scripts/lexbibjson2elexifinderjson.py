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
import spacy
sp = spacy.load('en_core_web_sm') # SpaCy English NLP module
from flashtext import KeywordProcessor
keyword_processor = KeywordProcessor()

# import stopword processor
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
stopWords = set(stopwords.words('english')) #adds standard English stopwords
 #add extra stopwords here: disturbing terms
stopWords.update({'example', 'context'})
 #add extra stopwords here: disturbing language names
stopWords.update({'even', 'axi', 'e', 'car', 'day', 'duke', 'en', 'toto', 'male', 'boon', 'bali', 'yoke', 'hu', 'u', 'gen', 'label', 'are', 'as', 'are', 'doe', 'fore', 'to', 'bit', 'bete', 'dem', 'mono', 'sake', 'pal', 'au', 'na', 'notre', 'rien', 'lui', 'papi', 'ce', 'sur', 'dan', 'busa', 'ki', 'were', 'ir', 'idi', 'kol', 'fut', 'maria', 'mano', 'ata', 'fur', 'lengua', 'mon', 'para', 'haya', 'war', 'garo', 'tera', 'sonde', 'amis', 'fam', 'pe', 'mari', 'laura', 'duma', 'lame', 'crow', 'nage', 'ha', 'pero', 'piu', 'ese', 'carrier', 'alas', 'ali', 'kis', 'lou' })
#print(stopWords)

# load subject list
with open('D:/LexBib/rdf2json/keyextractlist.json', encoding="utf-8") as infile:
	terms = json.load(infile, encoding="utf-8")
	keydict = {}
	print(terms)
	for term in terms:
		uri = term['uri']
		label = term['label']
		#print(label)
		if label.lower() not in list(stopWords):
			keydict[uri] = [label]
		else:
			print('Skipped term '+uri+' ('+label+')')
	#print(keydict)
# feed subject list to KeywordProcessor
	keyword_processor.add_keywords_from_dict(keydict)


# build subject dictionary with labels for Elexifinder
with open('D:/LexBib/rdf2json/erkeys.json', encoding="utf-8") as infile:
	terms = json.load(infile, encoding="utf-8")
	subjdict = {}
	for term in terms:
		subjdict[term['subject_uri']] = {'er_uri':term['er_uri'], 'er_label':term['er_label']}
	print(subjdict)



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

for item in bindings:
	itemuri = item['uri']['value']
	if itemuri not in useduri:
		itemcount += 1
		target = {}
		target['uri'] = itemuri
		print('['+str(itemcount)+'] '+itemuri)
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
		if 'articleTM' in item:
			target['articleTm'] = item['articleTM']['value'][0:22]
		if 'modTM' in item:
			target['crawlTm'] = item['modTM']['value'][0:22]
		if 'zotItemUri' in item:
			zotItemUri = item['zotItemUri']['value']    #+'?usenewlibrary=0'
			target['details']['zotItemUri']=zotItemUri
		if 'collection' in item:
			collection = int(item['collection']['value'])
			target['details']['collection']=collection
			target['images']=['http://lexbib.org/images/collection_'+str(collection)+'.jpg']
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
					target['body'] = bodytxt
					#print("\nCaught full text from "+txtfile+" for "+target['uri'])
			except:
				print("File "+txtfile+" for "+target['uri']+" was supposed to be there but not found")
				pass
		else:
			bodytxt = ""
		if fulltextsource != "":
			target['details']['bodytxtstatus'] = fulltextsource

	# lemmatize english text or abstract
		bodylem = ""
		for token in sp(bodytxt):
			bodylem+=("%s " % token.lemma_)
	# remove stop words
		lemtokens = word_tokenize(bodylem)
		#print(lemtokens)
		cleantokens = []
		stopchars = re.compile('[0-9\/_\.:;,\(\)\[\]\{\}<>]') # tokens with these characters are skipped
		for token in lemtokens:
		   if stopchars.search(token) == None:
			   cleantokens.append(token)
		cleantext = ' '.join([str(x) for x in cleantokens])
		#print(cleantext)

	# keyword extraction
		if target['lang'] !="":
			if target['lang'][-3:] == "eng":
				keywords = keyword_processor.extract_keywords(cleantext)
				keywordsfreqsort = sorted(keywords,key=keywords.count,reverse=False)
				used = set()
				keywordset = [x for x in keywordsfreqsort if x not in used and (used.add(x) or True)]

		# result
		#print(keywordset)
		categoryset = []
		count=1
		for termuri in keywordset:
			#print(termuri)
			#print(subjdict[termuri])
			category = {'uri':subjdict[termuri]['er_uri'],'label':subjdict[termuri]['er_label'],'wgt':count/len(keywordset)}
			categoryset.append(category)
			count=count+1
		target['categories'] = categoryset


	#write to JSON
		elexifinder.append(target)
		print('['+str(itemcount)+'] term discovery done.')
	# if uri appears twice:
	else:
		print('\nItem '+itemuri+' is a duplicate, something is wrong with it.\n')
# end of item loop

with open(infile.replace('.json', '_EF.json'), 'w', encoding="utf-8") as json_file: # path to result JSON file
	json.dump(elexifinder, json_file, indent=2)
	print("\n=============================================\nCreated processed JSON file for "+infile+". Finished.\n\n"+str(txtfilecount)+" files from manual attachments, "+str(grobidcount)+" files from GROBID output, "+str(pdftxtcount)+" files from Zotero pdf2txt")
