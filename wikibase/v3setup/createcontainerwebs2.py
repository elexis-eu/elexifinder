import config
import lwb
import csv
import sparql

with open(config.datafolder+'containers/containers_noweb.txt', 'r', encoding="utf-8") as file:
	v2containers = file.read().split('\n')

	for v2container in v2containers:
		print('\nNow processing: '+v2container)
		query = """PREFIX lwb: <http://data.lexbib.org/entity/>
		PREFIX ldp: <http://data.lexbib.org/prop/direct/>
		PREFIX lp: <http://data.lexbib.org/prop/>
		PREFIX lps: <http://data.lexbib.org/prop/statement/>
		PREFIX lpq: <http://data.lexbib.org/prop/qualifier/>

		select ?web where {

  		lwb:"""+v2container+""" ldp:P3 ?web.}

		"""
		print("Waiting for LexBib v2 SPARQL...")
		sparqlresults = sparql.query('https://data.lexbib.org/query/sparql',query)
		print('Got data from LexBib v2 SPARQL.')
		#go through sparqlresults
		weburl = None
		for row in sparqlresults:
			sparqlitem = sparql.unpack_row(row, convert=None, convert_type={})
			print(str(sparqlitem))
			weburl = sparqlitem[0]
		if weburl:
			qid = lwb.getidfromlegid("Q12", v2container)
			statement = lwb.updateclaim(qid, "P44", weburl, "url")
		else:
			print('Operation failed for: '+v2container)
