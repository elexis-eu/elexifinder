import lxml
from xml.etree import ElementTree
import re
import os
import sys
sys.path.insert(1, os.path.realpath(os.path.pardir))
import time
import json

infile = "D:/Lab_LexBib/elex-2021/procs.xml"

tree = ElementTree.parse(infile)
root = tree.getroot()
for outerdiv in root:
	item = {'title':None,'authors':[],'pdf':None,'pages':None}
	for middlediv in outerdiv:
		for innerdiv in middlediv:
			#print(innerdiv.attrib)
			if innerdiv.attrib['class'].startswith("av_textblock_section"):

				textarea = innerdiv.find('div')
				for par in textarea:
					title = par.findall('strong')
					if len(title) > 0:
						item['title'] = title[0].text
					authors = par.findall('em')
					if len(authors) > 0:
						item['authors'] = authors[0].text.split(", ")

			elif innerdiv.attrib['class'].startswith("avia-button-wrap"):
				item['pdf'] = innerdiv.find('a').attrib['href']
				item['pages'] = re.search(r'_pp([^\.]+).pdf', item['pdf']).group(1)

	with open("D:/Lab_LexBib/elex-2021/procs_parsed.jsonl", "a", encoding="utf-8") as jsonlfile:
		jsonlfile.write(json.dumps(item)+'\n')

print ('\nFinished.')
