import time
import re
import json
import csv
from collections import OrderedDict
from datetime import datetime
import sys
import os
import sparql
import json

sys.path.insert(1, os.path.realpath(os.path.pardir))
import lwb
import config

inverse_props = [
["P135", "P124"], # replaces / isReplacedWith
["P133", "P144"], # isVersionOf / hasVersion
["P125", "P143"], # isPartOf / hasPart
["P140", "P63"], # isContinuationOf / isContinuedBy
#["P55"], # has distribution /
#["P118"], # has realisation
]
index = 0
for reverse_pair in inverse_props:
	print('\nNow processing property pair: ', str(reverse_pair))
	index = 0
	while index < 2:
		if index == 0:
			pair = [reverse_pair[0], reverse_pair[1]]
			print('First run.')
		else:
			pair = [reverse_pair[1], reverse_pair[0]]
		print(str(pair))
		print('Checking direction '+pair[0]+' to '+pair[1]+'...')
		print('Running query: get '+pair[0]+' statements where '+pair[1]+' statement is not present...\n')
		query = config.lwb_prefixes + """
		PREFIX owl: <http://www.w3.org/2002/07/owl#>
		select distinct ?n ?nLabel ?b ?bLabel (REPLACE(STR(?redirect),".*Q","Q") AS ?redirect_qid)

		where {
		  ?n ldp:"""+pair[0]+""" ?b.
		  ?n rdfs:label ?nLabel . FILTER (lang(?nLabel)="en")

		  {?b rdfs:label ?bLabel . filter (lang(?bLabel)="en")}
		  UNION
		  {?b owl:sameAs ?redirect.}

		  filter not exists { ?b ldp:"""+pair[1]+""" ?n . }


		#  {?redirect rdfs:label ?rLabel .}UNION {?b rdfs:label ?rLabel .}FILTER (lang(?rLabel)="en")
		  }
		"""
		#print(query)

		url = "https://lexbib.elex.is/query/sparql"
		print("Waiting for SPARQL...")
		sparqlresults = sparql.query(url, query)
		print('\nGot term list from LexBib SPARQL.')

		# go through sparqlresults
		rowindex = 0

		for row in sparqlresults:
		    rowindex += 1
		    item = sparql.unpack_row(row, convert=None, convert_type={})
		    print('\nNow processing item [' + str(rowindex) + ']...')
		    print(str(item))
		    narrower_uri = item[0].replace("http://lexbib.elex.is/entity/", "")
		    narrower_label = item[1]
		    broader_uri = item[2].replace("http://lexbib.elex.is/entity/", "")
		    broader_label = item[3]
		    redirect_qid = item[4]
		    if redirect_qid != None:  # broader-rel points to redirect item
		        if redirect_qid.startswith("Q"):
		            print('Updating ' + broader_uri + ' redirect with ' + redirect_qid + '...')
		            broaderclaims = lwb.getclaims(narrower_uri, pair[0])[1]
		            if pair[0] in broaderclaims:
		                broaderstatement = broaderclaims[pair[0]][0]['id']
		                lwb.setclaimvalue(broaderstatement, redirect_qid, "item")
		                print('Updating relation: ' + narrower_uri + ' "' + str(broader_label) + pair[1] + str(
		                    narrower_label) + '"...')
		                lwb.updateclaim(redirect_qid, pair[1], narrower_uri, "item")
		        else:
		            print('Strange: for ' + broader_uri + ' I got redirect: ' + redirect_qid)
		    else:
		        print(
		            'Updating relation: ' + narrower_uri + ' "' + broader_label + pair[1] + narrower_label + '"...')
		        lwb.updateclaim(broader_uri, pair[1], narrower_uri, "item")

		index += 1



	# query = config.lwb_prefixes + """
	#
	# select distinct ?n ?nLabel ?narstatement ?b ?bLabel
	#
	# where {
	#   ?b ldp:"""+pair[1]+""" ?n .
	#   ?n rdfs:label ?nLabel . FILTER (lang(?nLabel)="en")
	#   filter not exists { ?n ldp:"""+pair[0]+""" ?b . }
  	#   ?b rdfs:label ?bLabel . FILTER (lang(?bLabel)="en")
	#
	#   }
	# """
	# print(query)
	#
	# url = "https://lexbib.elex.is/query/sparql"
	# print("Waiting for SPARQL...")
	# sparqlresults = sparql.query(url, query)
	# print('\nGot term list from LexBib SPARQL.')
	#
	# # go through sparqlresults
	# rowindex = 0
	#
	# for row in sparqlresults:
	#     rowindex += 1
	#     item = sparql.unpack_row(row, convert=None, convert_type={})
	#     print('\nNow processing item [' + str(rowindex) + ']\n')
	#     narrower_uri = item[0].replace("http://lexbib.elex.is/entity/", "")
	#     narrower_label = item[1]
	#     narstatement = item[2].replace("http://lexbib.elex.is/entity/statement/", "")
	#     broader_uri = item[3].replace("http://lexbib.elex.is/entity/", "")
	#     broader_label = item[4]
	#     print('Removing orphaned '+pair[1]+'-rel: "' + broader_label + pair[1] + narrower_label + '"...')
	#     lwb.removeclaim(narstatement)
