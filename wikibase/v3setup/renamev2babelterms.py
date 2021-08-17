import os
import lwb
import config
import time

with open(config.datafolder+'terms/lexbiblegacybnterms.txt', 'r') as infile:
	items_to_update = infile.read().split('\n')
print('\n'+str(len(items_to_update))+' items will be updated.')

path = 'D:/LexBib/babelnet/'
print('BabelNet Folder contains: '+str(os.listdir(path)))
for item in items_to_update:
	if item+'.json' in os.listdir(path):
		newqid = lwb.getidfromlegid("Q7", item, onlyknown=True)
		if newqid:
			print('Will rename '+item+' to '+newqid)
			newfile = newqid+'.json'
			if newfile not in os.listdir(path):
				os.rename(path+item+'.json',path+newfile)
				print('Performed renaming.\n')
			else:
				print('File already there, skipped.')
		else:
			print('Skipped v2 orphan term.')
			time.sleep(1)
