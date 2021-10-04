import lxml
from xml.etree import ElementTree
import re
import os
import sys
sys.path.insert(1, os.path.realpath(os.path.pardir))
import time
import json

download_dir = 'D:/LexBib/lexonomy/download'
completed = {}
stats = {}

skipcount = 0
processcount = 0
errorcount = 0

for path, dirs, files in os.walk(download_dir):
	for infile in files:

		dicname = re.search('^[^\.]+', infile).group(0)
		langcode = re.search('lexvoc\-([a-z]{3})', dicname).group(1)
		if langcode not in stats:
			stats[langcode] = {'prefLabels':0,'altLabels':0}
		if not (infile.endswith(".xml")):
			continue
		tree = ElementTree.parse(os.path.join(path, infile))
		root = tree.getroot()
		for entry in root:
			#time.sleep(2)
			termqid = entry.attrib['lexbib_id']
			for translation in entry.findall("translation"):
				statusl = translation.findall("status_translation")
				status = statusl[0].text
				if status == "COMPLETED":
					if termqid not in completed:
						completed[termqid] = {}
					if langcode not in completed[termqid]:
						completed[termqid][langcode] = {}
					labels = translation.findall("label")
					completed[termqid][langcode]['prefLabel'] = labels[0].text
					stats[langcode]['prefLabels'] += 1
					completed[termqid][langcode]['altlabels'] = []
					altlabels = translation.findall("altlabel")
					for altlabel in altlabels:
						completed[termqid][langcode]['altlabels'].append(altlabel.text)
						stats[langcode]['altLabels'] += 1

with open('D:/LexBib/lexonomy/completed_translations.json', "w", encoding="utf-8") as jsonfile:
	json.dump(completed, jsonfile, indent=2)
with open('D:/LexBib/lexonomy/completed_translations_stats_'+time.strftime("%Y%m%d-%H%M%S")+'.json', "w", encoding="utf-8") as jsonfile:
	json.dump(stats, jsonfile, indent=2)


print ('\nFinished. '+str(errorcount)+' errors, '+str(skipcount)+' skipped, '+str(processcount)+' processed.')
