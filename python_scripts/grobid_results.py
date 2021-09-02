# looks for .tei.xml files (grobid output) in a parent folder, adds body text clean version to same subfolder, by dlindem.

import lxml
from xml.etree import ElementTree
import re
import shutil
from bs4 import BeautifulSoup
import os
import time

upload_dir = 'D:/LexBib/zot2wb/grobid_upload'
download_dir = 'D:/LexBib/zot2wb/grobid_download'
zotero_dir = 'D:/Zotero/storage'
with open('D:/LexBib/zoteroapi/zotero_api_key.txt', 'r', encoding='utf-8') as pwdfile:
	zotero_api_key = pwdfile.read()

skipcount = 0
processcount = 0
errorcount = 0

for path, dirs, files in os.walk(download_dir):
	for infile in files:
		folder = os.path.dirname(infile)
		textname = re.search('^[^\.]+', infile).group(0)
		if infile.endswith(".tei.xml"):
			if os.path.exists(os.path.join(path, textname+"_grobidbody.txt")):
				print('Text '+textname+' in '+path+' is already processed, skipped.')
				skipcount = skipcount + 1
			else:
				tree = ElementTree.parse(os.path.join(path, infile))
				root = tree.getroot()
				ns = re.match(r'{.*}', root.tag).group(0)
				body = ElementTree.tostring(root[1][0])

				if (root[1][0].tag) == "{http://www.tei-c.org/ns/1.0}body":
					soup = BeautifulSoup(body, features="lxml")
					bodytext = re.sub(r'\n ', '\n', ' '.join(soup.find_all(text=True)).replace('  ',' '))
				else:
					print('\n\nFile '+infile+' is strange, body not found.\n\n')
					time.sleep(5)
					errorcount = errorcount + 1
				cleanfilename = infile.replace('.tei.xml','_grobidbody.txt')
				with open (os.path.join(path, cleanfilename), 'w', encoding="utf-8") as cleanfile:
					cleanfile.write(bodytext)

					shutil.copy(os.path.join(path, infile), os.path.join(path.replace(download_dir,zotero_dir), folder, infile))
					shutil.copy(os.path.join(path, cleanfilename), os.path.join(path.replace(download_dir,zotero_dir), folder, cleanfilename))
					#shutil.rmtree(os.path.join(download_dir,folder)
					shutil.rmtree(os.path.join(upload_dir,folder))

					print('Text '+textname+' in '+path+' has been processed, txt version saved, cleaned from grobid upload dir.')

					# # attach new grobid-produced text body to zotero item
					# attachment = [
					# {
					# "itemType": "attachment",
					# "parentItem": folder,
					# "linkMode": "imported_file",
					# "title": "GROBID text body",
					# "accessDate": "",
					# "note": "",
					# "tags": ["grobid_automatic"],
					# "collections": [],
					# "relations": {},
					# "contentType": "text/plain",
					# "charset": "utf-8",
					# "filename": cleanfilename
					# }
					# ]
					#
					# r = requests.post('https://api.zotero.org/groups/1892855/items', headers={"Zotero-API-key":zotero_api_key, "Content-Type":"application/json"} , json=attachment)


					processcount = processcount + 1

print ('\nFinished. '+str(errorcount)+' errors, '+str(skipcount)+' skipped, '+str(processcount)+' processed.')
