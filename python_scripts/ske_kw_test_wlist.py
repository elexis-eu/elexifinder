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
		print(corpname)
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
				print(refcorpname)

		# get word list
		for doc in range(len(ske_log[corpus]['docs'])):
			docname = ske_log[corpus]['docs'][doc]
			corpus_id_str = ske_log[corpus]
			subcname = "QS3CQ3UR_coll17_2017_manual_txt"
			#subcname = docname.replace(" ", "_").replace("/","_").lower()
			print('Now request for wordlist for subc '+subcname)
			k = requests.get("https://api.sketchengine.eu/bonito/run.cgi/wordlist?corpname=preloaded/bnc2;wlattr=lemma;wlsort=f;format=json")
			# k = requests.get("https://api.sketchengine.eu/bonito/run.cgi/wordlist", auth=ske_auth,
			# json={
			# "wltype":"simple", # for two-word term candidates, or "attr":"lemma" for one-word term candidates, right?
			# "corpname": corpname, # example "LexBib/Elexifinder v8 cat", must I rename to "LexBib_Elexifinder_v8_cat" or something, or add a path?
			# #"usesubcorp": subcname, # example "QS3CQ3UR_coll17_2017_manual_txt"
			# "format": "json",
			# "wlattr": "lemma",
			# "wlnums": "frq",
			# "wlsort": "f"
			# })
			print(str(k))
			print(str(k.content))
			kjson = json.loads(k.content.decode('utf8'))
			print(str(kjson))
			count += 1


print ('Finished getting keywords & terms from '+str(count)+' subcorpora.')
