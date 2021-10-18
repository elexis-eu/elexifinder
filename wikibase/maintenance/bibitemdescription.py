# creates descriptions for all instances of a class
import time
import requests
import os
import sys
sys.path.insert(1, os.path.realpath(os.path.pardir))
import lwb
import config
import json
import re

try:
	with open(config.datafolder+'/logs/bibitemdesc_doneitems.txt', 'r') as donelistfile:
		donelist = donelistfile.read().split('\n')
except:
	donelist = []

print('Will now get a list of all bibitems that have disambiguated creators, that are not reviews nor community comms nor event reports nor videos nor LCR distributions, and their description (if present)...')

url = "https://lexbib.elex.is/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fqualifier%2F%3E%0APREFIX%20lpr%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Freference%2F%3E%0APREFIX%20lno%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fnovalue%2F%3E%0A%0Aselect%20distinct%20%3FbibItem%20%3Fdesc%20where%0A%7B%20%3FbibItem%20ldp%3AP5%20lwb%3AQ3%3B%0A%20%20%20%20%20%20%20%20%20%20%20ldp%3AP12%7Cldp%3AP13%20%3Fcreator.%0A%20OPTIONAL%7B%3FbibItem%20schema%3Adescription%20%3Fdesc.%20filter%28lang%28%3Fdesc%29%3D%22en%22%29%7D%0A%20filter%20not%20exists%20%7B%3FbibItem%20ldp%3AP5%20lwb%3AQ15.%7D%20%23%20no%20reviews%0A%20filter%20not%20exists%20%7B%3FbibItem%20ldp%3AP5%20lwb%3AQ26.%7D%20%23%20no%20community%20communications%0A%20filter%20not%20exists%20%7B%3FbibItem%20ldp%3AP5%20lwb%3AQ46.%7D%20%23%20no%20event%20reports%0A%20filter%20not%20exists%20%7B%3FbibItem%20ldp%3AP5%20lwb%3AQ24.%7D%20%23%20no%20LCR%20distributions%0A%20filter%20not%20exists%20%7B%3FbibItem%20ldp%3AP100%20lwb%3AQ30.%7D%20%23%20no%20videos%0A%20%0A%20%20%7D"
done = False
while (not done):
	try:
		r = requests.get(url)
		bindings = r.json()['results']['bindings']
	except Exception as ex:
		print('Error: SPARQL request failed: '+str(ex))
		time.sleep(2)
		continue
	done = True
#print(str(bindings))

print('Found '+str(len(bindings))+' instances.\n')
time.sleep(3)

count = 0
for item in bindings:
	count +=1
	lwbitem = item['bibItem']['value'].replace("http://lexbib.elex.is/entity/","")
	print('\nWill now process ['+str(count)+']: '+lwbitem)
	if lwbitem in donelist:
		print('Item appears in donelist, skipped.')
		continue
	if 'desc' in item:
		desc = item['desc']['value']
		if desc.startswith("Publication by"):
			print('This item is already done.')
			with open(config.datafolder+'/logs/bibitemdesc_doneitems.txt', 'a') as donelistfile:
				donelistfile.write(lwbitem+'\n')
				continue

	# get item data

	url= """https://lexbib.elex.is/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fqualifier%2F%3E%0APREFIX%20lpr%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Freference%2F%3E%0APREFIX%20lno%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fnovalue%2F%3E%0A%0Aselect%20%3FbibItem%20%28YEAR%28%3Fdate%29%20as%20%3Fyear%29%0A%28group_concat%28distinct%20concat%28%27%7B%22lang%22%3A%22%27%2Cstr%28lang%28%3Ftitle%29%29%2C%27%22%2C%20%22text%22%3A%22%27%2C%3Ftitlestr%2C%27%22%7D%27%29%3BSEPARATOR%3D%22%2C%22%29%20as%20%3Ftitles%29%0A%28group_concat%28distinct%20concat%28%27%7B%22listpos%22%3A%22%27%2C%3Flistpos%2C%27%22%2C%20%22name%22%3A%22%27%2C%3FlastName%2C%27%22%7D%27%29%3BSEPARATOR%3D%22%2C%22%29%20as%20%3Fcreators%29%0Awhere%0A%7B%20BIND%20%28lwb%3A"""+lwbitem+"""%20as%20%3FbibItem%29%0A%20%3FbibItem%20ldp%3AP6%20%3Ftitle%20%3B%0A%20%20%20%20%20%20%20%20%20%20ldp%3AP15%20%3Fdate%20%3B%0A%20%20%20%20%20%20%20%20%20%20lp%3AP12%7Clp%3AP13%20%3Fcreatorstatement%20.%0A%20%3Fcreatorstatement%20lpq%3AP33%20%3Flistpos%3B%0A%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20%20lps%3AP12%7Clps%3AP13%20%3Fcreator.%0A%20%3Fcreator%20ldp%3AP102%20%3FlastName.%0A%20BIND%28REPLACE%28STR%28%3Ftitle%29%2C%27%22%27%2C%22%27%22%29%20AS%20%3Ftitlestr%29%20%0A%20%0A%20%20%7D%20group%20by%20%3FbibItem%20%3Fdate%20%3Ftitles%20%3Fcreators"""
	done = False
	while (not done):
		try:
			r = requests.get(url)
			itembindings = r.json()['results']['bindings']
		except Exception as ex:
			print('Error: SPARQL request failed: '+str(ex))
			time.sleep(2)
			continue
		done = True
	print(str(itembindings))

	if len(itembindings) != 1:
		print('Error, should have got one result, got '+str(len(itembindings)))
		with open(config.datafolder+'/logs/bibitemdesc_errors.txt', 'a') as errorfile:
			errorfile.write(lwbitem+'\n')
		with open(config.datafolder+'/logs/bibitemdesc_doneitems.txt', 'a') as donelistfile:
			donelistfile.write(lwbitem+'\n')
		count +=1
		continue
	year = itembindings[0]['year']['value']
	#titlesstring = itembindings[0]['titles']['value'])
	titles = json.loads('['+itembindings[0]['titles']['value']+']')
	creators = json.loads('['+itembindings[0]['creators']['value']+']')

	# set label from P6 title

	titledone = False
	for title in titles:
		if title['lang'] == "en":
			enlabel = title['text']
			titledone = True
	if (not titledone):
		enlabel = titles[0]['text']
	lwb.setlabel(lwbitem,"en",enlabel)

	# set description from authors, year

	print(str(creators))
	if len(creators) == 0:
		print('This item has no P12|P13 creator, skipped.')
		continue
	if len(creators) > 3:
		for creator in creators:
			if int(creator['listpos']) == 1:
				names = creator['name']+" et al. "
	else:
		names = ""
		for listpos in range(len(creators)):
			#print(str(listpos+1))
			for creator in creators:
				if int(creator['listpos']) == listpos+1:
					names += creator['name']
					if listpos+2 == len(creators):
						names += " & "
					elif listpos+3 == len(creators):
						names += ", "
					elif listpos+1 == len(creators):
						names += " "
	desc = "Publication by "+names+'('+year+')'
	print(desc)
	description = lwb.setdescription(lwbitem,"en",desc)
	if description:
		print('OK. '+str(len(bindings)-count)+' items left.')
		with open(config.datafolder+'/logs/bibitemdesc_doneitems.txt', 'a') as donelistfile:
			donelistfile.write(lwbitem+'\n')
