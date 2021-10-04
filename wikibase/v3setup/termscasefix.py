import sys
import os
sys.path.insert(1, os.path.realpath(os.path.pardir))
import config
import lwb
import csv
import re
import time


with open(config.datafolder+'terms/uppercasefix.csv', 'r', encoding="utf-8") as csvfile:
	terms = csv.DictReader(csvfile)
	count = 0
	for term in terms:
		count += 1
		print('\n['+str(count)+']:')


		termqid = term['Qid']
		enlabel = term['Len']
		lwb.setlabel(termqid, "en", enlabel, type="label")



		print('Item done: '+termqid+": "+enlabel+'\n')
