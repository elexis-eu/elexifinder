import sys
#2import lwb
import config
import time
import re
import requests
from pyzotero import zotero
pyzot = zotero.Zotero(1892855,'group',config.zotero_api_key)
#changed_items = lwb.getchangeditems('Q3','2021-08-14T20:07:22Z'):

zotitemtypes = [
"book",
"journalArticle",
"conferencePaper",
"bookSection"
]
print('\nSelect zotero item type for the items to batch edit:\n')
for num in range(len(zotitemtypes)):
	print('['+str(num+1)+'] '+zotitemtypes[num])

try:
	zotitemtype = zotitemtypes[int(input())-1]
	print('Selected item type: '+zotitemtype)
except Exception as ex:
	print ('Error: invalid selection.')
	print(str(ex))
	sys.exit()
pass

itemtemplate = requests.get("https://api.zotero.org/items/new?itemType="+zotitemtype).json()

itemkeys = list(itemtemplate.keys())

skip_keys = ["itemType", "creators", "tags", "collections", "relations"]
for x in skip_keys:
	itemkeys.remove(x)

print('\nSelect zotero JSON key to batch edit:\n')
for num in range(len(itemkeys)):
	print('['+str(num+1)+'] '+itemkeys[num])

try:
	targetkey = itemkeys[int(input())-1]
	print('Selected JSON key: '+targetkey)
except Exception as ex:
	print ('Error: invalid selection.')
	print(str(ex))
	sys.exit()
pass

# print('\nEnter the tag you chose for the batch to update:')
# targettag = input()
targettag = "_fix" #":container Q4849"

confirm = False
while confirm != "y":
	print('\nEnter the value you want to write to "'+targetkey+'":')
	updatevalue = input()
	print('Value will be:\n\n'+updatevalue+'\n\nConfirm entering "y":')
	confirm = input()
print('\nWill start to perform the update:')

zotitems_to_update = pyzot.items(tag=targettag)
#print(str(zotitems_to_update))
for item in zotitems_to_update:
	item['data'][targetkey] = updatevalue
	pyzot.update_item(item)
	print('Successfully written value to Zotero item '+item['key'])
	time.sleep(0.2)
