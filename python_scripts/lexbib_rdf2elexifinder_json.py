## treats output from LexBib RDF database (SPARQL query result as JSON, produced in VocBench3)
## these are snippets for keyword extraction tests performed with language names
## the file I actually use is lexbibjson2elexifinderjson.py

import re
import json
import spacy
import csv
sp = spacy.load('en_core_web_sm') # SpaCy English NLP module
from flashtext import KeywordProcessor
keyword_processor = KeywordProcessor()

# term matching (finding terms in text)
# first test gazetteer: English language names
# get language uri,label@en csv

with open('lexvo-iso639-3_english_labels.csv', encoding="utf-8") as infile:
	reader = csv.reader(infile)
	langdict = {}
	for rows in reader:
		if (len(str(rows[1]))>3):
			langdict[rows[0]] = [rows[1]]
print(langdict)
# feed language table to KeywordProcessor
keyword_processor.add_keywords_from_dict(langdict)
# import stopword processor
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
stopWords = set(stopwords.words('english')) #adds standard English stopwords
# stopWords.update({'undetermined'}) #add extra stopwords here
# print(stopWords)

with open("D:/Lab_LexDo/100520/result.json", encoding="utf-8") as f: # path to VocBench JSON SPARQL result
	data =  json.load(f, encoding="utf-16")
results = data['results']
bindings = results['bindings']

for item in bindings:
	if 'authorsJson' in item:
		authorsJson = item['authorsJson']
		authorsliteral = authorsJson['value']
		authors = json.loads(authorsliteral)
		item['authorsJson'] = authors
		item['authors'] = item.pop('authorsJson')
	if 'uri' in item:
		uri = item['uri']['value']
		item['uri'] = uri
	if 'title' in item:
		title = item['title']['value']
		item['title'] = title
	if 'articleTM' in item:
		articleTM = item['articleTM']['value']
		item['articleTM'] = articleTM
	# adding '?usenewlibrary=0' to Zotero Links
	if 'sourceUri' in item:
		sourceUri = item['sourceUri']['value']+'?usenewlibrary=0'
		item['sourceUri'] = sourceUri
	if 'sourceTitle' in item:
		sourceTitle = item['sourceTitle']['value']
		item['sourceTitle'] = sourceTitle
	if 'publang' in item:
		lang = item['publang']['value']
		item['lang'] = lang[-3:]
	bodytext = ""
	# check if text is English and txt-object exists
	if lang [-3:] == 'eng' and 'pdftxt' in item:
		txtpath = item['pdftxt']['value']
		try:
			with open(txtpath, 'r', encoding="utf-8") as txtfile:
				bodytext = txtfile.read()
			item['body'] = bodytext
		except IOError:
			print(title+" "+txtpath+" not accessible")
	else:
		print(title+" is "+lang+" ...aborted")
	# if fulltext was not English or not found, use english abstract (if exists)
	if bodytext == "" and 'abstracttext' in item and item['abstractlang']['value'][-3:] == 'eng':
		bodytext = item['abstracttext']['value']
		item['body'] = bodytext
		print(" - got abstract text instead")
	elif bodytext == "":
		print(" - found no English abstract")
	# lemmatize english text or abstract
	bodylem = ""
	for token in sp(bodytext):
		bodylem+=("%s " % token.lemma_)

	item['bodylem'] = bodylem
	# remove stop worsa
	lemtokens = word_tokenize(bodylem)
	print(lemtokens)
	cleantokens = []
	stopchars = re.compile('[0-9\/_\.]')
	for w in lemtokens:
	   if str(w).lower() not in stopWords and stopchars.search(str(w)) == None):
		   #print(w)
		   cleantokens.append(w)
	print (cleantokens)
	#find language names in english text
	#extract keywordset from text, in order of frequence, sub-order appeareance
	cleantext = ' '.join([str(x) for x in cleantokens])
	print(cleantext)
	keywords = keyword_processor.extract_keywords(cleantext)
	keywordsfreqsort = sorted(keywords,key=keywords.count,reverse=True)
	used = set()
	keywordset = [x for x in keywordsfreqsort if x not in used and (used.add(x) or True)]

	# result
	print(keywordset)

	# delete data not needed in Elexifinder JSON
	del item['abstractlang']
	del item['publang']
	del item['abstracttext']
	del item['pdftxt']



with open('D:/Lab_LexDo/100520/processed.json', 'w') as json_file: # path to result JSON file
	json.dump(bindings, json_file, indent=2)
