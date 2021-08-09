import mwclient
import traceback
import time
import sys
import os
import json
import re
#import requests
#import urllib.parse
import lwb
import config

# walk input dir

path = config.datafolder+"bibimport/"
dir_list = os.listdir(path)
# open and load input file

for infilename in dir_list:
	if infilename.endswith("_done.jsonl"):
		continue
	infile = os.path.join(path,infilename)
	print('This file will be processed: '+infile, infilename)
	try:
		with open(infile, encoding="utf-8") as f:
			jsonlines = f.read().split('\n')
			data = []
			for jsonline in jsonlines:
				try:
					data.append(json.loads(jsonline))
				except:
					pass
	except Exception as ex:
		print ('Error: file does not exist.')
		print (str(ex))
		sys.exit()

	totalrows = len(data)

	with open(config.datafolder+'logs/errorlog_'+infilename+'_'+time.strftime("%Y%m%d-%H%M%S")+'.log', 'w') as errorlog:
		index = 0
		edits = 0
		rep = 0

		while index < totalrows:
			if index >= 0: #start item in infile
				if rep > 4: # break 'while' loop after 5 failed attempts to process item
					print ('\nbibimport.py has entered in an endless loop... abort.')
					break
				else:
					print('\n'+str(index)+' items processed. '+str(totalrows-index)+' list items left.\n')
					#time.sleep(1)
					rep += 1
					zotitemstatement = None
					try:
						item = data[index]
						lexBibID = item['lexBibID']
						print('LexBibID is '+lexBibID)
						# if re.match(r'^Q\d+', item['lexbibLegacyID']):
						# 	legacyidstatement = lwb.updateclaim(lexBibID,"P1",item['lexbibLegacyID'],"string")
						# else:
						# 	print('*** There is an item without URI: ',str(item))
						# 	errorlog.write('\n*** There is an item without URI: '+str(item)+'\n')
						# 	# lexBibID = lwb.getqid("Q3", item['lexBibID']) # Q3: LexBib BibItem class
						if 'lexBibClass' in item and 'lexBibClass' != "":
							classStatement = lwb.updateclaim(lexBibID,"P5",item['lexbibClass'],"item")
						if "P12" in str(item['creatorvals']):
							skipeditors = True
						else:
							skipeditors = False
						for triple in item['creatorvals']:
							### check if creator with that position is already there as item (not literal)
							#skip = False
							# if triple['property'] == "P39":
							# 	itemprop = "P12"
							# elif triple['property'] == "P42":
							# 	itemprop = "P13"
							# for Qualifier in triple['Qualifiers']:
							# 	if Qualifier['property'] == "P33":
							# 		listpos = Qualifier['value']
							# 		print('Found '+triple['property']+' creator listpos: ',listpos)
							# claims = lwb.getclaims(lexBibID, itemprop)
							# lexBibID = claims[0]
							# creator_item_claims = claims[1]
							# if itemprop in creator_item_claims:
							# 	for creator_item_claim in creator_item_claims[itemprop]:
							# 		creator_item_listpos = creator_item_claim['qualifiers']["P33"][0]['datavalue']['value']
							# 		if creator_item_listpos == listpos:
							# 			print('Found creator literal already replaced with creator item, will skip.')
							# 			skip = True
							### if creator item claim for this creator listpos is not found, update literal
							if triple['property'] == "P13" and skipeditors == True:
								continue
							statement = lwb.updateclaim(lexBibID,triple['property'],triple['value'],triple['datatype'])
							if "Qualifiers" in triple:
								for qualitriple in triple['Qualifiers']:
									lwb.setqualifier(lexBibID,triple['property'],statement, qualitriple['property'], qualitriple['value'], qualitriple['datatype'])

						for triple in item['propvals']:
							if triple['property'] == "P8":
								continue
							if triple['property'] == "P16":
								zotitemid = triple['value']
								zotitemstatement = lwb.updateclaim(lexBibID,triple['property'],triple['value'],triple['datatype'])
							elif triple['property'] == "P70" or triple['property'] == "P71":
								if not zotitemstatement:
									zotitemstatement = lwb.getclaims(lexBibID,"P16")['P16'][0]['id']
								lwb.setqualifier(lexBibID,"P16",zotitemstatement,triple['property'],triple['value'],triple['datatype'])
							else:
								statement = lwb.updateclaim(lexBibID,triple['property'],triple['value'],triple['datatype'])
							if "Qualifiers" in triple:
								for qualitriple in triple['Qualifiers']:
									lwb.setqualifier(lexBibID,triple['property'],statement, qualitriple['property'], qualitriple['value'], qualitriple['datatype'])

					except Exception as ex:
						traceback.print_exc()
						lwb.logging.error('bibimport.py: Error at input line ['+str(index+1)+'] '+item['lexBibID']+':'+str(ex))
						continue

					rep = 0
			index += 1

	print('\nFinished this infile: '+infilename+'. Check error log.')
	os.rename(infile,infile.replace(".jsonl","_done.jsonl"))
