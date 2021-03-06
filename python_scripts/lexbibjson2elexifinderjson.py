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

# import stopword processor
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
stopWords = set(stopwords.words('english')) #adds standard English stopwords
 #add extra stopwords here: disturbing terms
stopWords.update({'example', 'context'})
 #add extra stopwords here: disturbing language names
stopWords.update({'even', 'axi', 'e', 'car', 'day', 'duke', 'en', 'toto', 'male', 'boon', 'bali', 'yoke', 'hu', 'u', 'gen', 'label', 'are', 'as', 'are', 'doe', 'fore', 'to', 'bit', 'bete', 'dem', 'mono', 'sake', 'pal', 'au', 'na', 'notre', 'rien', 'lui', 'papi', 'ce', 'sur', 'dan', 'busa', 'ki', 'were', 'ir', 'idi', 'kol', 'fut', 'maria', 'mano', 'ata', 'fur', 'lengua', 'mon', 'para', 'haya', 'war', 'garo', 'tera', 'sonde', 'amis', 'fam', 'pe', 'mari', 'laura', 'duma', 'lame', 'crow', 'nage', 'ha', 'pero', 'piu', 'ese', 'carrier', 'alas', 'ali', 'kis', 'lou', '—' })
print(stopWords)

# load subject list
with open('D:/LexBib/terms/er_skos_3levelcats_dic.json', encoding="utf-8") as infile:
	terms = json.load(infile, encoding="utf-8")

for stop in list(stopWords):
	if stop in terms:
		del terms[stop]

keydict = {}
subjdict = {}
for term in terms:
	for lexi in terms[term]:
		print(str(lexi))
		keydict[lexi['subject_uri']] = [lexi['subjectLabel']]
		subjdict[lexi['subject_uri']] = {'er_uri':lexi['er_uri'], 'er_label':lexi['er_label']}

print(keydict)
print(subjdict)
# feed subject list to KeywordProcessor
keyword_processor.add_keywords_from_dict(keydict)


# build subject dictionary with labels for Elexifinder

# subjdict = {}
# for term in terms:
# 	for lexi in terms:
# 	subjdict[terms[term]['subject_uri']] = {'er_uri':terms[term]['er_uri'], 'er_label':terms[term]['er_label']}
# print(subjdict)

# load abstract dictionary
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
	itemuri = item['uri']['value']
	if itemuri not in useduri:
		itemcount += 1
		target = {}
		target['uri'] = itemuri
		print('\n['+str(itemcount)+'] '+itemuri)
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
		else:
			print ('*** ERROR: mandatory key articleTM not in '+itemuri+'!')
			problemlog.append('*** ERROR: mandatory key articleTM not in '+itemuri+'!\n')
		if 'modTM' in item:
			target['crawlTm'] = item['modTM']['value'][0:22]
		if 'zotItemUri' in item:
			zotItemUri = item['zotItemUri']['value']    #+'?usenewlibrary=0'
			target['details']['zotItemUri']=zotItemUri
			target['url'] = zotItemUri
		else:
			print ('*** ERROR: mandatory key zotItemUri not in '+itemuri+'!')
			problemlog.append('*** ERROR: mandatory key zotItemUri not in '+itemuri+'!\n')
		if 'collection' in item:
			collection = int(item['collection']['value'])
			target['details']['collection']=collection
			if collection in images:
				target['images']=images[collection]
			else:
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
				target['details']['keywords'] = keywords
			#	keywordsfreqsort = sorted(keywords,key=keywords.count,reverse=False)
			#	used = set()
			#	keywordset = [x for x in keywordsfreqsort if x not in used and (used.add(x) or True)]

				# result
				categorylist = []
				#print(keywords)
				for keyword in keywords:
					categorylist.append(subjdict[keyword]['er_uri']+'@'+subjdict[keyword]['er_label'])
				#print(categorylist)
				catsfreqsort = sorted(categorylist,key=categorylist.count,reverse=False)
				used = set()
				catset = [x for x in catsfreqsort if x not in used and (used.add(x) or True)]
				#print (catset)
				categoryexport = []
				count=1
				for cat in catset:
					caturilabel = cat.split('@')
					category = {'uri':caturilabel[0],'label':caturilabel[1],'wgt':count/len(catset)}
					categoryexport.append(category)
					count=count+1
				target['categories'] = categoryexport
				print('...['+str(itemcount)+'] was English text; term discovery done.')
			else:
				print('...['+str(itemcount)+'] was not English text; term discovery skipped.')


	#write to JSON
		elexifinder.append(target)

	# if uri appears twice:
	else:
		print('\nItem '+itemuri+' is a duplicate, something is wrong with it.\n')
		problemlog.append('{"'+itemuri+'", "multiple attachments"}')

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
