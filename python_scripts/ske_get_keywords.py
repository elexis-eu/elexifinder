#!/usr/bin/python
import json
import requests
import time
import babel_lang_codes

with open('D:/LexBib/SkE/pwd.txt', 'r', encoding='utf-8') as pwdfile:
	pwd = pwdfile.read()

ske_auth = ('jsi_api', pwd)
ske_url = 'https://api.sketchengine.eu/ca/api'

with open('D:/LexBib/SkE/ske_dict.json', 'r', encoding='utf-8') as skelogfile:
	ske_log = json.load(skelogfile)
	print("ske_log: "+str(len(ske_log))+" corpora\n")

with open('D:/LexBib/SkE/ske_languages.json', 'r', encoding='utf-8') as skelangfile:
	ske_lang = json.load(skelangfile)

count = 0
for corpus in ske_log:
	if 'docs' in ske_log[corpus]:

		corpname = corpus.replace(" ","_").replace("/","_")
		if "cat" not in corpname:
			continue
		corpus_url = ske_log[corpus]['corpus_url']
		corplang = ske_log[corpus]['language']
		babellang = babel_lang_codes.langcodemapping[corplang].lower()
		print('Now processing corpus for language '+corplang+': '+corpname)
		for lang in ske_lang['data']:
			#print(lang['id'])
			if lang['id'] == babellang:
				refcorpname = lang['reference_corpus']

		# get keywords and terms
		for doc in range(len(ske_log[corpus]['docs'])):
			docname = ske_log[corpus]['docs'][doc]
			corpus_id_str = ske_log[corpus]
			subcname = corpname.replace(" ", "_").replace("/","_").lower()
			print('Now request for keywords for subc '+subcname)
			k = requests.get("https://api.sketchengine.eu/bonito/run.cgi/extract_keywords?attr=lemma&corpname"+subcname+"&format=json&max_keywords=100&minfreq=3&ref_corpname="+refcorpname, auth=ske_auth)
			kjson = json.loads(k.content.decode('utf8'))
			print(str(kjson))
			print('Now request for terms for subc '+subcname)
			t = requests.get("https://api.sketchengine.eu/bonito/run.cgi/extract_terms?attr=lemma&corpname"+subcname+"&format=json&ref_corpname="+refcorpname, auth=ske_auth)
			tjson = json.loads(t.content.decode('utf8'))
			print(str(tjson))
			# for item in kjson['keywords']:
			# 	print(item['item'])
			# 	print(item['score'])
			# for item in tjson['keywords']:
			# 	print(item['item'])
			# 	print(item['score'])
			count += 1


print ('Finished getting keywords & terms from '+str(count)+' subcorpora.')
