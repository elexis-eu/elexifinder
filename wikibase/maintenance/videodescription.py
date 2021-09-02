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

print('Will now get a list of all videos and their container short titles.')

url = "https://lexbib.elex.is/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fqualifier%2F%3E%0APREFIX%20lpr%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Freference%2F%3E%0APREFIX%20lno%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fnovalue%2F%3E%0A%0Aselect%20distinct%20%3Fvideo%20%3Fconttitle%20where%0A%7B%20%3Fvideo%20ldp%3AP100%20lwb%3AQ30%3B%0A%20%20%20%20%20%20%20%20%20%20%20ldp%3AP9%20%3Fcontainer.%0A%20%3Fcontainer%20ldp%3AP97%20%3Fconttitle.%7D"
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
	lwbitem = item['video']['value'].replace("http://lexbib.elex.is/entity/","")
	conttitle = item['conttitle']['value']
	print('\nWill now process ['+str(count)+']: '+lwbitem)
	desc = "A video presentation at "+conttitle
	description = lwb.setdescription(lwbitem,"en",desc)
	if description:
		print('OK. '+str(len(bindings)-count)+' items left.\n')
		
