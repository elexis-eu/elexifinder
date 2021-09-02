#!/usr/bin/python
import json
import requests
import time

with open('D:/LexBib/SkE/pwd.txt', 'r', encoding='utf-8') as pwdfile:
	pwd = pwdfile.read()

ske_auth = ('jsi_api', pwd)
ske_url = 'https://beta.sketchengine.eu/ca/api'

with open('D:/LexBib/SkE/ske_dict.json', 'r', encoding='utf-8') as skelogfile:
	ske_log = json.load(skelogfile)
	print("ske_log: "+str(len(ske_log))+" corpora\n")

count = 0
for corpus in ske_log:
	if 'docs' in ske_log[corpus]:

		corpname = corpus.replace(" ","_").replace("/","_")
		corpus_url = ske_log[corpus]['corpus_url']
		print('Now processing corpus for language '+ske_log[corpus]['language']+': '+corpname)

		# configure corpus
		while True:
			try:
				r = requests.put(corpus_url, auth=ske_auth, json={'file_structure': 'elexifinder_doc', 'docstructure': 'elexifinder_doc'})
				if "200" in str(r):
					print('Corpus '+corpname+' configured.')
					break
				else:
					print (str(r))
			except Exception as ex:
				print(str(ex))

		# write rules
		rules = ""
		for doc in range(len(ske_log[corpus]['docs'])):
			docname = ske_log[corpus]['docs'][doc]
			rules += '='+docname+'\nelexifinder_doc\nfilename="'+docname+'"\n\n'
		rulesjson = '{"'+rules+'"}'

		# write rules to SkE
		while True:
			try:
				r = requests.put(corpus_url + '/subcdef', auth=ske_auth, headers={'content-type': 'text/plain'}, json=rules)
				if "200" in str(r):
					print('Corpus '+corpname+': rules written to SkE.')
					break
				else:
					print (str(r))
					print (str(r.content))
			except Exception as ex:
				print(str(ex))

		# write rules to file
		rulefile = 'D:/LexBib/SkE/subc_rules/'+corpname
		with open(rulefile, 'w', encoding='utf-8') as outfile:
			outfile.write(rules)


		# trigger corpus compilation
		while True:
			try:
				r = requests.post(corpus_url + '/compile', json={'structures': 'all'}, auth=ske_auth)
				if "200" in str(r):
					print('Corpus compilation successfully triggered.')
					break
				else:
					print (str(r))
			except Exception as ex:
				print(str(ex))



		count += 1

print ('Finished writing subc rules to '+str(count)+' corpora.')
