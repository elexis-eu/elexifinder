#!/usr/bin/python
import json
import requests
import time

with open('D:/LexBib/SkE/pwd.txt', 'r', encoding='utf-8') as pwdfile:
	pwd = pwdfile.read()

auth = ('jsi_api', pwd)
URL = 'https://api.sketchengine.eu/ca/api'

with open('D:/LexBib/SkE/ske_dict.json', 'r', encoding='utf-8') as skelogfile:
	ske_log = json.load(skelogfile)
	print("ske_log: "+str(len(ske_log))+" corpora\n")

count = 0
for corpus in ske_log:
	if 'docs' in ske_log[corpus]:

		corpname = corpus.replace(" ","_").replace("/","_")
		rulefile = 'D:/LexBib/SkE/subc_rules/'+corpname
		with open(rulefile, 'w', encoding='utf-8') as outfile:
			for doc in range(len(ske_log[corpus]['docs'])):
				print(str(doc))
				#print(ske_log[corpus]['docs'])

				docname = ske_log[corpus]['docs'][doc]
				outfile.write('='+docname+'\nlexbibdoc\nfilename="'+docname+'"\n\n')
				count += 1



print ('Finished writing '+str(count)+' rules.')
