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
	with open(config.datafolder+'/logs/langitemdesc_doneitems.txt', 'r') as donelistfile:
		donelist = donelistfile.read().split('\n')
except:
	donelist = []

print('Will now get a list of all languages that have no description or no isocode in their description...')

url = "https://lexbib.elex.is/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fqualifier%2F%3E%0APREFIX%20lpr%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Freference%2F%3E%0APREFIX%20lno%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fnovalue%2F%3E%0A%0Aselect%20distinct%20%3Flang%20%3Fdesc%20%3Fiso%20where%0A%7B%7B%20%3Flang%20ldp%3AP5%20lwb%3AQ8%3B%20%0A%20%20%20%20%20%20%20%20%20ldp%3AP32%20%3Fiso%3B%0A%20%20%20%20%20%20%20%20%20schema%3Adescription%20%3Fdesc.%20filter%28lang%28%3Fdesc%29%3D%22en%22%29%0A%20filter%20%28strstarts%28%3Fdesc%2C%22%5B%22%29%20%3D%20False%29%7D%0Aunion%20%0A%7B%20%3Flang%20ldp%3AP5%20lwb%3AQ8%3B%20ldp%3AP32%20%3Fiso.%0A%20%20filter%20not%20exists%20%7B%3Flang%20%20schema%3Adescription%20%3Fdesc.%20filter%28lang%28%3Fdesc%29%3D%22en%22%29%7D%0A%20%7D%0A%0A%20%0A%20%20%7D"
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
	lwbitem = item['lang']['value'].replace("http://lexbib.elex.is/entity/","")
	print('\nWill now process ['+str(count)+']: '+lwbitem)
	if lwbitem in donelist:
		print('Item appears in donelist, skipped.')
		continue
	if 'desc' in item:
		desc = item['desc']['value']
		if desc.startswith("["):
			print('This item is already done.')
			with open(config.datafolder+'/logs/langitemdesc_doneitems.txt', 'a') as donelistfile:
				donelistfile.write(lwbitem+'\n')
				continue
	iso = item['iso']['value']
	description = lwb.setdescription(lwbitem,"en","["+iso+"], a natural language")
	if description:
		print('OK. '+str(len(bindings)-count)+' items left.')
		with open(config.datafolder+'/logs/langitemdesc_doneitems.txt', 'a') as donelistfile:
			donelistfile.write(lwbitem+'\n')
