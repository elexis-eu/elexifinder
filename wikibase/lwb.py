import mwclient
import json
import urllib.parse
import time
import re
import csv
import requests
import sys
import unidecode
import sparql
import logging
from wikidataintegrator import wdi_core, wdi_login
import config

# Properties with constraint: max. 1 value
max1props = config.max1props

# Logging config
logging.basicConfig(filename=config.datafolder+'logs/lwb.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%m-%y %H:%M:%S')

#WDI setup

with open(config.datafolder+'wikibase/'+config.lwbuser+'_pwd.txt', 'r', encoding='utf-8') as pwdfile:
	lwbbotpass = pwdfile.read()
mediawiki_api_url = "https://lexbib.elex.is/w/api.php" # <- change to applicable wikibase
sparql_endpoint_url = "https://lexbib.elex.is/query/sparql"  # <- change to applicable wikibase
wdilogin = wdi_login.WDLogin(config.lwbuser, lwbbotpass, mediawiki_api_url=mediawiki_api_url)
lwbEngine = wdi_core.WDItemEngine.wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)
print('Logged into WDI.')

# LexBib wikibase OAuth for mwclient
with open(config.datafolder+'wikibase/'+config.lwbuser+'_pwd.txt', 'r', encoding='utf-8') as pwdfile:
	lwbbotpass = pwdfile.read()
site = mwclient.Site('lexbib.elex.is')
def get_token():
	global site
	global lwbbotpass
	# lwb login via mwclient
	while True:
		try:
			login = site.login(username=config.lwbuser, password=lwbbotpass)
			break
		except Exception as ex:
			print('lwb login via mwclient raised error: '+str(ex))
			time.sleep(60)
	# get token
	csrfquery = site.api('query', meta='tokens')
	token = csrfquery['query']['tokens']['csrftoken']
	print("Got fresh CSRF token for lexbib.elex.is.")
	return token
token = get_token()

# Loads known lwbqid-lexbibUri mappings and lwbqid-Wikidataqid mappins from jsonl-files
def load_legacyID():
	legacyID = {}
	try:
		with open(config.datafolder+'mappings/legacymappings.jsonl', encoding="utf-8") as jsonl_file:
			mappings = jsonl_file.read().split('\n')
			count = 0
			for mapping in mappings:
				count += 1
				if mapping != "":
					try:
						mappingjson = json.loads(mapping)
						#print(mapping)
						legacyID[mappingjson['legacyID']] = mappingjson['lwbid']
					except Exception as ex:
						print('Found unparsable mapping json in legacymappings.jsonl line ['+str(count)+']: '+mapping)
						print(str(ex))
						pass
	except Exception as ex:
		print ('Error: legacyID file does not exist. Will start a new one.')
		print (str(ex))
	#print(str(legacyID))
	print('Known LWB Qid loaded.')
	return legacyID
legacyID = load_legacyID()

def load_wdmappings():
	wdids = {}
	try:
		with open(config.datafolder+'mappings/lwb_wd.jsonl', encoding="utf-8") as f:
			mappings = f.read().split('\n')
			count = 0
			for mapping in mappings:
				count += 1
				if mapping != "":
					try:
						mappingjson = json.loads(mapping)
						#print(mapping)
						wdids[mappingjson['lwbid']] = mappingjson['wdid']
					except Exception as ex:
						print('Found unparsable mapping json in lwb_wd.jsonl line ['+str(count)+']: '+mapping)
						print(str(ex))
						pass
	except Exception as ex:
		print ('Error: wdmappings file does not exist. Will start a new one.')
		print (str(ex))

	print('Known LWB-WD item mappings loaded.')
	return wdids
wdids = load_wdmappings()

def load_wppageplaces():
	wpplaces = {}
	try:
		with open(config.datafolder+'mappings/wppage_lwbplace.jsonl', encoding="utf-8") as f:
			mappings = f.read().split('\n')
			count = 0
			for mapping in mappings:
				count += 1
				if mapping != "":
					try:
						mappingjson = json.loads(mapping)
						#print(mapping)
						wpplaces[mappingjson['wppage']] = mappingjson['lwbid']
					except Exception as ex:
						print('Found unparsable mapping json in wppage_lwbplace.jsonl line ['+str(count)+']: '+mapping)
						print(str(ex))
						pass
	except Exception as ex:
		print ('Error in load_wppageplaces function.')
		print (str(ex))

	print('Known wikipedia places loaded.')
	return wpplaces

# Adds a new lexbibUri-qid mapping to legacyID.jsonl mapping file
def save_legacyID(legid,lwbid):
	with open(config.datafolder+'mappings/legacymappings.jsonl', 'a', encoding="utf-8") as jsonl_file:
		jsonline = {"legacyID":legid,"lwbid":lwbid}
		jsonl_file.write(json.dumps(jsonline)+'\n')
		global legacyID
		legacyID[legid] = lwbid

# Adds a new lwbqid-wdqid mapping to wdmappings.jsonl mapping file
def save_wdmapping(mapping): # example {"lwbid": "P32", "wdid": "P220"}
	with open(config.datafolder+'mappings/lwb_wd.jsonl', 'a', encoding="utf-8") as jsonl_file:
		jsonl_file.write(json.dumps(mapping)+'\n')
	global wdids
	wdids[mapping['lwbid']] = mapping['wdid']


# Get equivalent lwb item qidnum from wikidata Qid
def wdid2lwbid(wdid):
	print('Will try to find lwbqid for '+wdid+'...')
	global wdids
	# Try to find lwbqid from known mappings
	for key, value in wdids.items():
		if wdid == value:
			print('Found lwbqid in wdids known mappings: '+key)
			return key
	# # Try to find lwbqid via SPARQL
	# url = "https://lexbib.elex.is/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fdirect%2F%3E%0A%0Aselect%20%3FlwbItem%20where%0A%7B%20%3FlwbItem%20ldp%3AP4%20wd%3A"+wdid+"%20.%20%7D"
	#
	# while True:
	# 	try:
	# 		r = requests.get(url)
	# 		lwbqid = r.json()['results']['bindings'][0]['lwbItem']['value'].replace("http://lexbib.elex.is/entity/","")
	# 	except Exception as ex:
	# 		print('Error: SPARQL request failed.')
	# 		time.sleep(2)
	# 		return False
	# 	break
	# print('Found lwbqid '+lwbqid+' not in mappingfile, but via SPARQL, will add it to mappingfile.')
	# save_wdmapping({'lwbid':lwbqid, 'wdid':wdqid})
	# return lwbqid
	print('*** Found no lwbid for '+wdid)
	return None

# creates a new item
def newitemwithlabel(lwbclasses, labellang, label): # lwbclass: object of 'instance of' (P5)
	global token
	global legacyID
	if isinstance(lwbclasses, str) == True: # if a single value is passed as string, not as list
		lwbclasses = [lwbclasses]
	data = {"labels":{labellang:{"language":labellang,"value":label}}}
	done = False
	while (not done):
		try:
			itemcreation = site.post('wbeditentity', token=token, new="item", bot=True, data=json.dumps(data))
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			else:
				print(str(ex))
				time.sleep(4)
			continue
		#print(str(itemcreation))
		if itemcreation['success'] == 1:
			done = True
			qid = itemcreation['entity']['id']
			print('Item creation for '+qid+': success. Label: '+label)
		else:
			print('Item creation failed, will try again...')
			time.sleep(2)

		for lwbclass in lwbclasses:
			done = False
			while (not done):
				claim = {"entity-type":"item","numeric-id":int(lwbclass.replace("Q",""))}

				try:
					classclaim = site.post('wbcreateclaim', token=token, entity=qid, property="P5", snaktype="value", value=json.dumps(claim))
					if classclaim['success'] == 1:
						done = True
						print('Instance-of-claim creation for '+qid+': success. Class is '+lwbclass)
						#time.sleep(1)
				except:
					print('Claim creation failed, will try again...')
					if "Invalid CSRF token" in str(ex):
						print('Wait a sec. Must get a new CSRF token...')
						token = get_token()
					time.sleep(2)
		return qid



# function for wikibase item creation (after check if it is known)
#token = get_token()
def getidfromlegid(lwbclasses, legid, onlyknown=False): # lwbclass: object of 'instance of' (P5), legid = value of (P1), pointing to data.lexbib.org legacy item id
	global token
	global legacyID
	if isinstance(lwbclasses, str) == True: # if a single value is passed as string, not as list
		lwbclasses = [lwbclasses]
	if legid in legacyID:
		print(legid+'(v2) is a known v3 item: Qid '+legacyID[legid]+'.')
		return legacyID[legid]

	# check if this is a redirect
	query = """PREFIX lwb: <http://data.lexbib.org/entity/>
	PREFIX owl: <http://www.w3.org/2002/07/owl#>
	select (REPLACE(STR(?redirect),".*Q","Q") AS ?redirect_qid) where {
	lwb:"""+legid+""" owl:sameAs ?redirect.}"""
	print("Waiting for LexBib v2 SPARQL (check redirect for "+legid+")...")
	sparqlresults = sparql.query('https://data.lexbib.org/query/sparql',query)
	print('Got data for this from LexBib v2 SPARQL.')

	#go through sparqlresults

	try:
		for row in sparqlresults:
			sparqlitem = sparql.unpack_row(row, convert=None, convert_type={})
			print(str(sparqlitem))
			v2redir = str(sparqlitem[0])
			print("Found v2 redirect: "+v2redir)
			if sparqlitem[0].startswith("Q") and v2redir in legacyID:
				redir = legacyID[v2redir]
				print("Found redirect: "+redir)
				return redir
	except Exception as ex:
		print(str(ex))
		pass

	if onlyknown:
		return None

	print('Found no Qid for LexBib URI '+legid+', will create it.')
	claim = {"claims":[{"mainsnak":{"snaktype":"value","property":"P1","datavalue":{"value":legid,"type":"string"}},"type":"statement","rank":"normal"}]}
	done = False
	while (not done):
		try:
			itemcreation = site.post('wbeditentity', token=token, new="item", bot=1, data=json.dumps(claim))
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			else:
				print(str(ex))
				time.sleep(4)
			continue
		#print(str(itemcreation))
		if itemcreation['success'] == 1:
			done = True
			qid = itemcreation['entity']['id']
			print('Item creation for v2 '+legid+': success. QID = '+qid)
		else:
			print('Item creation failed, will try again...')
			time.sleep(2)



	for lwbclass in lwbclasses:
		done = False
		while (not done):
			claim = {"entity-type":"item","numeric-id":int(lwbclass.replace("Q",""))}
			classclaim = site.post('wbcreateclaim', token=token, entity=qid, property="P5", snaktype="value", value=json.dumps(claim))
			try:
				if classclaim['success'] == 1:
					done = True
					print('Instance-of-claim creation for '+legid+': success. Class is '+lwbclass)
					#time.sleep(1)
			except:
				print('Claim creation failed, will try again...')
				time.sleep(2)
	legacyID[legid] = qid
	save_legacyID(legid,qid)
	return qid

#get label
def getlabel(qid, lang):
	done = False
	while True:
		request = site.get('wbgetentities', ids=qid, props="labels", languages=lang)
		if request['success'] == 1:
			return request["entities"][qid]["labels"][lang]["value"]
		else:
			print('Something went wrong with label retrieval for '+qid+', will try again.')
			time.sleep(3)

#get label
def getaliases(qid, lang):
	done = False
	while True:
		request = site.get('wbgetentities', ids=qid, props="aliases", languages=lang)
		if request['success'] == 1:
			aliases = []
			if lang in request["entities"][qid]["aliases"]:
				aliaslist = request["entities"][qid]["aliases"][lang]
				for alias in aliaslist:
					aliases.append(alias['value'])
			return aliases
		else:
			print('Something went wrong with aliases retrieval for '+qid+', will try again.')
			time.sleep(3)

#create item claim
def itemclaim(s, p, o):
	global token

	done = False
	value = json.dumps({"entity-type":"item","numeric-id":int(o.replace("Q",""))})
	while (not done):
		try:
			request = site.post('wbcreateclaim', token=token, entity=s, property=p, snaktype="value", value=value, bot=1)
			if request['success'] == 1:
				done = True
				claimId = request['claim']['id']
				print('Claim creation done: '+s+' ('+p+') '+o+'.')
				#time.sleep(1)
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			else:
				print('Claim creation failed, will try again...\n'+str(ex))
				time.sleep(4)
	return claimId

#create string (or url) claim
def stringclaim(s, p, o):
	global token

	done = False
	value = '"'+o.replace('"', '\\"')+'"'
	while (not done):
		try:
			request = site.post('wbcreateclaim', token=token, entity=s, property=p, snaktype="value", value=value, bot=1)
			if request['success'] == 1:
				done = True
				claimId = request['claim']['id']
				print('Claim creation done: '+s+' ('+p+') '+o+'.')
				#time.sleep(1)
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			else:
				print('Claim creation failed, will try again...\n'+str(ex))
				time.sleep(4)
	return claimId

#create string (or url) claim
def setlabel(s, lang, val, type="label"):
	global token

	done = False
	count = 0
	value = val # insert operations if necessary
	while count < 5:
		count += 1
		try:
			if type == "label":
				request = site.post('wbsetlabel', id=s, language=lang, value=value, token=token, bot=1)
			elif type == "alias":
				request = site.post('wbsetaliases', id=s, language=lang, add=value, token=token, bot=1)
			if request['success'] == 1:
				print('Label creation done: '+s+' ('+lang+') '+val+', type: '+type)
				return True
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			elif 'Unrecognized value for parameter "language"' in str(ex):
				print('Cannot set label in this language: '+lang)
				logging.warning('Cannot set label in this language: '+lang)
				break
			else:
				print('Label set operation '+s+' ('+lang+') '+val+' failed, will try again...\n'+str(ex))
				logging.error('Label set operation '+s+' ('+lang+') '+val+' failed, will try again...', exc_info=True)
				time.sleep(4)
	# log.add
	print ('*** Label set operation '+s+' ('+lang+') '+val+' failed up to 5 times... skipped.')
	logging.warning('Label set operation '+s+' ('+lang+') '+val+' failed up to 5 times... skipped.')
	return False

#create string (or url) claim
def setdescription(s, lang, val):
	global token

	done = False
	count = 0
	value = val # insert operations if necessary
	while count < 5:
		count += 1
		try:
			request = site.post('wbsetdescription', id=s, language=lang, value=value, token=token, bot=1)
			if request['success'] == 1:
				print('Description creation done: '+s+' ('+lang+') "'+val+'".')
				return True
		except Exception as ex:
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			elif 'Unrecognized value for parameter "language"' in str(ex):
				print('Cannot set description in this language: '+lang)
				logging.warning('Cannot set description in this language: '+lang)
				break
			elif 'already has label' in str(ex) and 'using the same description text.' in str(ex):
				# this is a hot candidate for merging
				print('*** Oh, it seems that we have a hot candidate for merging here... Writing info to mergecandidates.log')
				with open ('logs/mergecandidates.log', 'a', encoding='utf-8') as mergecandfile:
					mergecand = re.search(r'\[\[Item:(Q\d+)',str(ex)).group(1)
					mergecandfile.write(s+' and '+mergecand+' : '+val+'\n')
				break
			else:
				print('Description set operation '+s+' ('+lang+') '+val+' failed, will try again...\n'+str(ex))
				logging.error('Description set operation '+s+' ('+lang+') '+val+' failed, will try again...', exc_info=True)
				time.sleep(4)
	# log.add
	print ('*** Description set operation '+s+' ('+lang+') '+val+' failed up to 5 times... skipped.')
	logging.warning('Description set operation '+s+' ('+lang+') '+val+' failed up to 5 times... skipped.')
	return False

#get claims from qid
def getclaims(s, p):
	done = False
	while (not done):
		#print('will try to get claims now for '+s)
		try:
			if p == True: # get all claims
				request = site.get('wbgetclaims', entity=s)
			else:
				request = site.get('wbgetclaims', entity=s, property=p)
			if "claims" in request:
				done = True
				#print('Getclaims will return: '+s, request['claims'])
				return (s, request['claims'])
		except Exception as ex:
			if 'unresolved-redirect' in str(ex):

				#get redirect target
				url = "https://lexbib.elex.is/query/sparql?format=json&query=PREFIX%20lwb%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fentity%2F%3E%0APREFIX%20ldp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fdirect%2F%3E%0APREFIX%20lp%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2F%3E%0APREFIX%20lps%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fstatement%2F%3E%0APREFIX%20lpq%3A%20%3Chttp%3A%2F%2Flexbib.elex.is%2Fprop%2Fqualifier%2F%3E%0A%0Aselect%20%28strafter%28str%28%3Fredirect%29%2C%22http%3A%2F%2Flexbib.elex.is%2Fentity%2F%22%29%20as%20%3Frqid%29%20where%0A%7Blwb%3AQ2874%20owl%3AsameAs%20%3Fredirect.%7D%0A%20%20%0A"
				subdone = False
				while (not subdone):
					try:
						r = requests.get(url)
						bindings = r.json()['results']['bindings']
					except Exception as ex:
						print('Error: SPARQL request for redirects failed: '+str(ex))
						time.sleep(2)
						continue
					subdone = True

				if 'rqid' in bindings[0]:
					print('Found redirect target '+bindings[0]['rqid']['value']+', will use that instead.')
					s = bindings[0]['rqid']['value']
					continue


			print('Getclaims operation failed, will try again...\n'+str(ex))
			time.sleep(4)

#get claim from statement ID
def getclaimfromstatement(guid):
	done = False
	while (not done):
		try:
			request = site.get('wbgetclaims', claim=guid)

			if "claims" in request:
				done = True
				return request['claims']
		except Exception as ex:
			print('Getclaims operation failed, will try again...\n'+str(ex))
			time.sleep(4)

#update claims
def updateclaim(s, p, o, dtype): # for novalue: o="novalue", dtype="novalue"
	global max1props
	global token
	returnvalue = None
	language = None
	if dtype == "time":
		data=[(wdi_core.WDTime(o['time'], prop_nr=p, precision=o['precision']))]
		item = lwbEngine(wd_item_id=s, data=data)
		print('Successful time object write operation to item '+item.write(wdilogin))
		# TBD: duplicate statement control
		claims = getclaims(s,p)
		#print(str(claims))
		return claims[1][p][0]['id']
	elif dtype == "string" or dtype == "url":
		value = '"'+o.replace('"', '\\"')+'"'
	elif dtype == "monolingualtext":
		value = json.dumps({"text":o['text'],"language":o['language']})
	elif dtype == "item" or dtype =="wikibase-entityid":
		value = json.dumps({"entity-type":"item","numeric-id":int(o.replace("Q",""))})
	elif dtype == "novalue":
		value = "novalue"

	claims = getclaims(s,p)
	s = claims[0]
	claims = claims[1]
	foundobjs = []
	if claims and bool(claims):
		statementcount = 0
		for claim in claims[p]:
			statementcount += 1
			guid = claim['id']
			#print(str(claim['mainsnak']))
			if claim['mainsnak']['snaktype'] == "value":
				foundo = claim['mainsnak']['datavalue']['value']
			elif claim['mainsnak']['snaktype'] == "novalue":
				foundo = "novalue"
			if isinstance(foundo, dict) and 'id' in foundo: # foundo is a dict with "id" as key in case of datatype wikibaseItem
				#print(str(foundo))
				foundo = foundo['id']
			if foundo in foundobjs:
				print('Will remove a duplicate claim: '+guid)
				results = site.post('wbremoveclaims', claim=guid, token=token)
				if results['success'] == 1:
					print('Wb remove duplicate claim for '+s+' ('+p+') '+str(o)+': success.')
			else:
				foundobjs.append(foundo)
				#print("A statement #"+str(statementcount)+" for prop "+p+" is already there: "+foundo)

				if foundo == o or foundo == value:
					print('Found redundant triple ('+p+') '+str(o)+' >> Claim update skipped.')
					returnvalue = guid



				if p in max1props:
					if returnvalue and len(foundobjs) > 1:
						print('There is a second statement for a max1prop. Will delete that.')
						results = site.post('wbremoveclaims', claim=guid, token=token)
						if results['success'] == 1:
							print('Wb remove duplicate claim for '+s+' ('+p+') '+str(o)+': success.')
							foundobjs.remove(foundo)
					elif not returnvalue:
						print('('+p+') is a max 1 prop. Will replace statement.')

						while True:
							try:
								results = site.post('wbsetclaimvalue', token=token, claim=guid, snaktype="value", value=value)

								if results['success'] == 1:
									print('Claim update for '+s+' ('+p+') '+str(o)+': success.')
									foundobjs.append(o)
									returnvalue = guid
									break
							except Exception as ex:
								if 'Invalid CSRF token.' in str(ex):
									print('Wait a sec. Must get a new CSRF token...')
									token = get_token()
								else:
									print('Claim update failed... Will try again.')
									time.sleep(4)

	if returnvalue:
		return returnvalue
	if o not in foundobjs and value not in foundobjs: # must create new statement

		count = 0
		while count < 5:
			count += 1
			try:
				if dtype == "novalue":
					request = site.post('wbcreateclaim', token=token, entity=s, property=p, snaktype="novalue", bot=1)
				else:
					request = site.post('wbcreateclaim', token=token, entity=s, property=p, snaktype="value", value=value, bot=1)

				if request['success'] == 1:

					claimId = request['claim']['id']
					print('Claim creation done: '+s+' ('+p+') '+str(o)+'.')
					return claimId

			except Exception as ex:
				if 'Invalid CSRF token.' in str(ex):
					print('Wait a sec. Must get a new CSRF token...')
					token = get_token()
				else:
					print('Claim creation failed, will try again...\n'+str(ex))
					logging.error('Claim creation '+s+' ('+p+') '+str(o)+' failed, will try again...\n', exc_info=True)
					time.sleep(4)

		print ('*** Claim creation operation '+s+' ('+p+') '+str(o)+' failed 5 times... skipped.')
		logging.warning('Label set operation '+s+' ('+p+') '+str(o)+' failed 5 times... skipped.')
		return False
	else:
		print('*** Unknown error in lwb.updateclaim function.')



# set a Qualifier
def setqualifier(qid, prop, claimid, qualiprop, qualivalue, dtype):
	global token
	if dtype == "string" or dtype == "url" or dtype == "monolingualtext":
		qualivalue = '"'+qualivalue.replace('"', '\\"')+'"'
	elif dtype == "item" or dtype =="wikibase-entityid":
		qualivalue = json.dumps({"entity-type":"item","numeric-id":int(qualivalue.replace("Q",""))})

	# claims = getclaims(qid,prop)
	# foundobjs = []
	# if bool(claims):
	# 	statementcount = 0
	# 	for claim in claims[prop]:
	# 		if claim['id'] == claimid:
	#
	try:
		while True:
			setqualifier = site.post('wbsetqualifier', token=token, claim=claimid, property=qualiprop, snaktype="value", value=qualivalue, bot=1)
			# always set!!
			if setqualifier['success'] == 1:
				print('Qualifier set ('+qualiprop+') '+qualivalue+': success.')
				return True
			print('Qualifier set failed, will try again...')
			logging.error('Qualifier set failed for '+prop+' ('+qualiprop+') '+qualivalue+': '+str(ex))
			time.sleep(2)

	except Exception as ex:
		if 'The statement has already a qualifier' in str(ex):
			print('**** The statement already has a ('+qualiprop+') '+qualivalue+' duplicate qualifier')
			return False




# set a Reference
def setref(claimid, refprop, refvalue, dtype):
	global token
	if dtype == "string" or dtype == "monolingualtext":
		#refvalue = '"'+refvalue.replace('"', '\\"')+'"'
		refvalue = refvalue.replace('"', '\\"')
		valtype = "string"
	elif dtype == "url":
		# no transformation
		valtype = "string"
	elif dtype == "item" or dtype =="wikibase-entityid":
		refvalue = json.dumps({"entity-type":"item","numeric-id":int(refvalue.replace("Q",""))})
		valtype = "wikibase-entityid"
	snaks = json.dumps({refprop:[{"snaktype":"value","property":refprop,"datavalue":{"type":valtype,"value":refvalue}}]})
	while True:
		try:
			setref = site.post('wbsetreference', token=token, statement=claimid, index=0, snaks=snaks, bot=1)
			# always set at index 0!!
			if setref['success'] == 1:
				print('Reference set for '+refprop+': success.')
				return True
		except Exception as ex:
			#print(str(ex))
			if 'The statement has already a reference with hash' in str(ex):
				print('**** The statement already has a reference (with the same hash)')
				time.sleep(1)
			else:
				logging.error('Unforeseen exception: '+str(ex))
				print(str(ex))
				time.sleep(5)
			return False


		print('Reference set failed, will try again...')
		logging.error('Reference set failed for '+prop+' ('+refprop+') '+refvalue+': '+str(ex))
		time.sleep(2)

# Function for getting wikipedia url from wikidata qid (from https://stackoverflow.com/a/60811917)
def get_wikipedia_url_from_wikidata_id(wikidata_id, lang='en', debug=False):
	#import requests
	from requests import utils

	url = (
		'https://www.wikidata.org/w/api.php?action=wbgetentities&props=sitelinks/urls&ids='+wikidata_id+'&format=json')
	json_response = requests.get(url).json()
	if debug: print(wikidata_id, url, json_response)

	entities = json_response.get('entities')
	if entities:
		entity = entities.get(wikidata_id)
		if entity:
			sitelinks = entity.get('sitelinks')
			if sitelinks:
				if lang:
					# filter only the specified language
					sitelink = sitelinks.get(lang+'wiki')
					if sitelink:
						wiki_url = sitelink.get('url')
						if wiki_url:
							return requests.utils.unquote(wiki_url)
				else:
					# return all of the urls
					wiki_urls = {}
					for key, sitelink in sitelinks.items():
						wiki_url = sitelink.get('url')
						if wiki_url:
							wiki_urls[key] = requests.utils.unquote(wiki_url)
					return wiki_urls
	return None

#remove claim
def removeclaim(guid):
	global token
	guidfix = re.compile(r'^(Q\d+)\-')
	guid = re.sub(guidfix, r'\1$', guid)
	done = False
	while (not done):
		try:
			results = site.post('wbremoveclaims', claim=guid, token=token)
			if results['success'] == 1:
				print('Wb remove claim for '+guid+': success.')
				done = True
		except Exception as ex:
			print('Removeclaim operation failed, will try again...\n'+str(ex))
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			if 'invalid-guid' in str(ex):
				print('The guid to remove was not found.')
				done = True
			time.sleep(4)

#remove claim
def removequali(guid, hash):
	global token
	done = False
	while (not done):
		try:
			results = site.post('wbremovequalifiers', claim=guid, qualifiers=hash, token=token)
			if results['success'] == 1:
				print('Wb remove qualifier success.')
				done = True
		except Exception as ex:
			print('Removequalifier operation failed, will try again...\n'+str(ex))
			if 'Invalid CSRF token.' in str(ex):
				print('Wait a sec. Must get a new CSRF token...')
				token = get_token()
			if 'no-such-qualifier' in str(ex):
				print('The qualifier to remove was not found.')
				done = True
			time.sleep(4)

# load property mapping and datatype list
def load_propmapping():
	query = """
	PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
	PREFIX wdno: <http://www.wikidata.org/prop/novalue/>
	PREFIX lno: <http://lexbib.elex.is/prop/novalue/>
	PREFIX lwb: <http://lexbib.elex.is/entity/>
	PREFIX ldp: <http://lexbib.elex.is/prop/direct/>
	PREFIX lp: <http://lexbib.elex.is/prop/>
	PREFIX lps: <http://lexbib.elex.is/prop/statement/>
	PREFIX lpq: <http://lexbib.elex.is/prop/qualifier/>
	PREFIX lpr: <http://lexbib.elex.is/prop/reference/>

	select ?order (REPLACE(str(?lwb_p), "http://lexbib.elex.is/entity/", "") as ?pid) ?datatype ?wdEquivProp (REPLACE(str(?range), "http://lexbib.elex.is/entity/", "") as ?p_range)
	where {
	  ?lwb_p rdf:type <http://wikiba.se/ontology#Property> ;
	     <http://wikiba.se/ontology#propertyType> ?datatype .
	  ?lwb_p ldp:P2 ?wdEquivProp.
	  OPTIONAL {?lwb_p ldp:P48 ?range}
	BIND (xsd:integer(REPLACE(str(?lwb_p), "http://lexbib.elex.is/entity/P", "")) as ?order )
	} group by ?order ?lwb_p ?datatype ?wdEquivProp ?range order by ?order
	"""
	print("Waiting for LexBib v3 SPARQL (load property mapping)...")
	sparqlresults = sparql.query('https://lexbib.elex.is/query/sparql',query)
	print('Got properties from LexBib v3 SPARQL.')
	#go through sparqlresults
	propmapping = {}
	for row in sparqlresults:
		sparqlitem = sparql.unpack_row(row, convert=None, convert_type={})
		pid = sparqlitem[1]
		propmapping[pid] = {}
		if sparqlitem[2]:
			propmapping[pid]['datatype'] = sparqlitem[2]
		if sparqlitem[3]:
			propmapping[pid]['wdid'] = sparqlitem[3]
		if sparqlitem[3]:
			propmapping[pid]['range'] = sparqlitem[4]
		print(str(propmapping))
	return propmapping
