import os
import json
import datetime
import re
import sys
sys.path.insert(1, os.path.realpath(os.path.pardir))
import langmapping

# load stats from files
stats_dir = "D:/LexBib/lexonomy/stats"
stats = {}
dates = []
for file in os.listdir(stats_dir):
	print(file)
	jsonfile = stats_dir+"/"+file
	date = file.replace("statistics-","").replace(".json","")
	date = re.sub(r'([0-9]{4}\-[0-9]{2})\-([0-9])$',r'\1-0\2',date)
	dates.append(date)
	with open(jsonfile, "r", encoding="utf-8") as statsfile:
		stats[date] = json.load(statsfile)
print('stats files loaded.')

# sort dates
print(str(dates))
dateobjs = [datetime.datetime.strptime(ts, "%Y-%m-%d") for ts in dates]
dateobjs.sort()
sorteddates = [datetime.datetime.strftime(ts, "%Y-%m-%d") for ts in dateobjs]

# produce data csv #1: line headings are dates, row headings are langs, cells are number of terms

langs = langmapping.langcodemapping.keys() # ELEXIS languages
csv = ","+",".join(langs)+"\n"
for date in sorteddates:
	csv += date
	for lang in langs:
		if lang in stats[date]['completed_langs']:
			csv += ","+str(len(stats[date]['completed_langs'][lang]))
		else:
			csv += ",0"
	csv += "\n"

print(csv)

with open("D:/LexBib/lexonomy/stats_csv.csv", "w", encoding="utf-8") as csvfile:
	csvfile.write(csv)
