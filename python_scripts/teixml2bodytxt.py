# looks for .tei.xml files (grobid output) in a parent folder, adds body text clean version to same subfolder, by dlindem.

import lxml
from xml.etree import ElementTree
import re
from bs4 import BeautifulSoup
import os

parent_dir = 'D:/LexBib/exports/export_filerepo'

skipcount = 0
processcount = 0
errorcount = 0

for path, dirs, files in os.walk(parent_dir):
    for infile in files:
        textname = re.search('^[^\.]+', infile).group(0)
        if infile.endswith(".tei.xml"):
            if os.path.exists(os.path.join(path, textname+"_body.txt")):
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
                    print('File '+infile+' is strange, body not found.')
                    errorcount = errorcount + 1
                with open (os.path.join(path, infile.replace('.tei.xml','_body.txt')), 'w', encoding="utf-8") as cleanfile:
                    cleanfile.write(bodytext)
                    print('Text '+textname+' in '+path+' has been processed, txt version saved.')
                    processcount = processcount + 1

print ('\nFinished. '+str(errorcount)+' errors, '+str(skipcount)+' skipped, '+str(processcount)+' processed.')
