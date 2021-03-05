#!/usr/bin/python
import json
import requests
import time
import sys

with open('D:/LexBib/SkE/pwd.txt', 'r', encoding='utf-8') as pwdfile:
	pwd = pwdfile.read()

ske_auth = ('jsi_api', pwd)
ske_url = 'https://beta.sketchengine.eu/ca/api'

print('Which version of LexBib/Elexifinder corpora do you want to trigger the compilation for? Type the number.')
try:
	version = int(input())
except:
	print ('Error: This has to be a number.')
	sys.exit()

with open('D:/LexBib/SkE/ske_dict.json', 'r', encoding='utf-8') as skelogfile:
	ske_log = json.load(skelogfile)
	print("ske_log: "+str(len(ske_log))+" corpora\n")

count = 0
for corpus in ske_log:
	if str(version) in ske_log[corpus] and 'docs' in ske_log[corpus]:
		corpname = corpus.replace(" ","_").replace("/","_")
		corpus_url = ske_log[corpus]['corpus_url']
		print('Now processing corpus for language '+ske_log[corpus]['language']+': '+corpname)
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

print ('Finished triggering compilation of '+str(count)+' corpora.')
