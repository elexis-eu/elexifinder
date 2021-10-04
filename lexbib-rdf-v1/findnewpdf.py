# finds pdf in a parent folder that have no .tei.xml and _body.txt pendant and copies them to a folder to upload, by dlindem

import shutil
import os
import glob
from distutils.dir_util import copy_tree

parent_dir = "D:/LexBib/exports/export_filerepo"

for path, dirs, files in os.walk(parent_dir):
	for dir in dirs:
		xmlfile = os.path.join(path, dir, '*tei.xml')
		#print (xmlfile)
		if glob.glob(xmlfile):
			#print (dir+' has a xml file '+str(os.listdir(os.path.join(path, dir))))
			pass
		else:
			if glob.glob(os.path.join(path, dir, '*.pdf')):
				copy_tree(os.path.join(path, dir), 'D:/LexBib/exports/PDF_grobidupload/'+dir)
				print('OK. Found PDF without tei pendant. Copied '+dir)
			else:
				print ('Strange. '+dir+' has no PDF.')

		#if os.path.exists(os.path.join(path, "*.tei.xml")) == False:
			#print (dir+' has no .tei.xml')
