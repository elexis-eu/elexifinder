import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv
import json

with open(config.datafolder+'terms/lexbibwdtermrefs.csv', 'r', encoding="utf-8") as csvfile:
	termrefs = csv.DictReader(csvfile)

	for termref in termrefs:

		claimid = termref['statement'].replace("http://lexbib.elex.is/entity/statement/","")
		print('\nClaim ID is: '+claimid)
		lwb.setref(claimid, "P2", termref['wd'], "string")
