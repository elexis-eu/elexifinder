from SPARQLWrapper import SPARQLWrapper, JSON
import time
import sys
import json
import requests
import mwclient
import sparql
import csv
import os
import sys
sys.path.insert(1, os.path.realpath(os.path.pardir))
import lwb
import config

classes_to_update = ["Q6", "Q34"]

with open(config.datafolder+"mappings/classes_props_schema.csv", "r", encoding="utf-8") as schemacsv:
	schema = csv.DictReader(schemacsv, delimiter=",")
	classes = []
	schemadict = {}
	for line in schema:
		for cl in line:
			if cl not in schemadict and line[cl] != "":
				schemadict[cl] = [line[cl]]
			elif line[cl] != "":
				schemadict[cl].append(line[cl])

print(str(schemadict))

propmapping = lwb.load_propmapping()

for c in schemadict:

	if c not in classes_to_update:
		continue

	print ('LWB class to be updated is: '+c)

	props = schemadict[c] 	# List of LWB properties to be taken values for from Wikidata

	# Get LWB items belonging to class c that have P2 (wdid) set
	query = """PREFIX lwb: <http://lexbib.elex.is/entity/>
	PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
	select * where
	{ ?item ldp:P5 lwb:"""+c+"""; ldp:P2 ?wdid .}"""
	print("Waiting for LexBib v3 SPARQL (load class "+c+" members)...")
	sparqlresults = sparql.query('https://lexbib.elex.is/query/sparql',query)
	print('Got data from LexBib v3 SPARQL.')
	#go through sparqlresults
	classmembers = []
	for row in sparqlresults:
		sparqlitem = sparql.unpack_row(row, convert=None, convert_type={})
		classmembers.append({"lwbid":sparqlitem[0],"wdid":sparqlitem[1]})
	print('Class '+c+' has '+str(len(classmembers))+' members with wdid P2 set.')
	wikidata = mwclient.Site('wikidata.org')

	for prop in props:
		print('\n-----------------------------------------------------\nNow beginning update for class '+c+', prop '+prop+'...')
		if prop == "P66": # get en.wikipedia url and write it to LWB using P66
			itemcount = 1
			for item in classmembers:
				print('\nItem ['+str(itemcount)+'], '+str(len(classmembers)-itemcount)+' items left.')
				wdqid = item['wdid']
				lwbqid = item['lwbid'].replace("http://lexbib.elex.is/entity/","")
				print('...will now get en.wikipedia page url for LWB item: '+lwbqid+' from wdItem: '+wdqid)
				enwikiurl = lwb.get_wikipedia_url_from_wikidata_id(wdqid, lang='en')#, debug=True)
				if enwikiurl:
					statement = lwb.updateclaim (lwbqid,"P66",enwikiurl,"url")
					reference = lwb.setref(statement,"P2",wdqid,"string")
				itemcount += 1
		elif prop == "Len": # get label (English), and write it to LWB
			itemcount = 1
			for item in classmembers:
				print('\nItem ['+str(itemcount)+'], '+str(len(classmembers)-itemcount)+' items left.')
				wdqid = item['wdid']
				lwbqid = item['lwbid'].replace("http://lexbib.elex.is/entity/","")
				print('...will now get label (English) for LWB item: '+lwbqid+' from wdItem: '+wdqid)
				done = False
				while (not done):
					try:
						r = requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=labels&ids="+wdqid+"&languages=en").json()
						#print(str(r))
						if "labels" in r['entities'][wdqid]:
							label = r['entities'][wdqid]['labels']['en']['value']
							done = True

					except Exception as ex:
						print('Wikidata: Getlabels operation failed, will try again...\n'+str(ex))
						time.sleep(4)

				lwb.setlabel (lwbqid,"en",label)
				itemcount += 1
		elif prop == "Den": # get description (English), and write it to LWB
			itemcount = 1
			for item in classmembers:
				print('\nItem ['+str(itemcount)+'], '+str(len(classmembers)-itemcount)+' items left.')
				wdqid = item['wdid']
				lwbqid = item['lwbid'].replace("http://lexbib.elex.is/entity/","")
				print('...will now get description (English) for LWB item: '+lwbqid+' from wdItem: '+wdqid)
				done = False
				while (not done):
					try:
						r = requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=descriptions&ids="+wdqid+"&languages=en").json()
						#print(str(r))
						if "descriptions" in r['entities'][wdqid]:
							if "en" in r['entities'][wdqid]["descriptions"]:
								desc = r['entities'][wdqid]['descriptions']['en']['value']
								done = True
							else:
								desc = None
								done = True

					except Exception as ex:
						print('Wikidata: Getdescription operation failed, will try again...\n'+str(ex))
						time.sleep(4)

				if desc:
					# update to setdesc >> lwb.setlabel (lwbqid,"en",label)
					# this will write to 'skos:definition' prop P80:
					statement = lwb.updateclaim(lwbqid,"P80",desc,"string")
					reference = lwb.setref(statement,"P2",wdid,"string")
				itemcount += 1
		else:
			# get wikidata equivalent prop
			try:
				wdprop = propmapping[prop]['wdid']
			except:
				print('*** No equivalent Wikidata property found for '+prop+'.')
				continue

			# get classmembers that have no statement for this property
			# Get LWB items belonging to class c that have P2 (wdid) set
			query = """PREFIX lwb: <http://lexbib.elex.is/entity/>
			PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
			select ?item ?wdid where
			{ ?item ldp:P5 lwb:"""+c+"""; ldp:P2 ?wdid .
			filter not exists{ ?item ldp:"""+prop+""" ?statement}}"""
			print("Waiting for LexBib v3 SPARQL (load class "+c+" members)...")
			sparqlresults = sparql.query('https://lexbib.elex.is/query/sparql',query)
			print('Got data from LexBib v3 SPARQL.')
			#go through sparqlresults
			classmembers_to_update = []
			for row in sparqlresults:
				sparqlitem = sparql.unpack_row(row, convert=None, convert_type={})
				classmembers_to_update.append({"lwbid":sparqlitem[0],"wdid":sparqlitem[1]})
			print('Class '+c+' has '+str(len(classmembers_to_update))+' members with wdid P2 and prop '+prop+' set.')

			itemcount = 1
			for item in classmembers_to_update:
				print('\nItem ['+str(itemcount)+'], '+str(len(classmembers_to_update)-itemcount)+' items left for this prop.')
				wdqid = item['wdid']
				lwbqid = item['lwbid'].replace("http://lexbib.elex.is/entity/","")
				print('...will now update LWB item: '+lwbqid+' from wdItem: '+wdqid)
				done = False
				while (not done):
					try:
						request = wikidata.get('wbgetclaims', entity=wdqid, property=wdprop)
					except Exception as ex:
						print('Wikidata: Getclaims operation failed, will try again...\n'+str(ex))
						time.sleep(4)
					if "claims" in request:
						done = True
						itemcount += 1
				if bool(request['claims']): # i.e. if claims is not empty and contains a list (of claims)
					for claim in request['claims'][wdprop]:
						if claim['mainsnak']['snaktype'] == "value":
							if 'qualifiers' in claim:
								if len(request['claims'][wdprop]) > 1 and "P582" in claim['qualifiers']:
									continue # skip claims that have an 'end time' P582 qualifier, in case there are various claims for this prop


							dtype = claim['mainsnak']['datavalue']['type']

							if dtype == "wikibase-entityid":
								wdoqid = claim['mainsnak']['datavalue']['value']['id']
								value = lwb.wdid2lwbid(wdoqid)
								print('wdid2lwbid returns: '+str(value))
								if not value: # if this wd item does not exist on lwb
									if 'range' in propmapping[prop]: # if we know its class, we can create a new orphanisation-proof item.
										range = propmapping[prop]['range']
										print('Will create new item of class '+str(range)+' (range of '+prop+').')
										if range:
											print('...will now get label (English) for wdItem: '+wdoqid)
											done = False
											while (not done):
												try:
													r = requests.get("https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&props=labels&ids="+wdoqid+"&languages=en").json()
													#print(str(r))
													if "labels" in r['entities'][wdoqid]:
														newlabel = r['entities'][wdoqid]['labels']['en']['value']
														done = True
												except Exception as ex:
													print('Wikidata: Getlabels operation failed, will try again...\n'+str(ex))
													time.sleep(4)
											newqid = lwb.newitemwithlabel(range, "en", newlabel)
											lwb.stringclaim(newqid, "P2", wdoqid)
											lwb.save_wdmapping({"lwbid": newqid, "wdid": wdoqid})
											value = newqid
							elif dtype == "time":
								value = {'time':claim['mainsnak']['datavalue']['value']['time'],'precision':claim['mainsnak']['datavalue']['value']['precision']}
							else:
								value = claim['mainsnak']['datavalue']['value']


							if value:
								statement = lwb.updateclaim(lwbqid,prop,value,dtype)
								reference = lwb.setref(statement,"P2",wdqid,"string")
							else:
								print('Could not write this statement (no value defined)')
				else:
					print('No claim on Wikidata.')
					itemcount += 1
