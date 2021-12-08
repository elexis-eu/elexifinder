import config
import sys
import math
from pyzotero import zotero
pyzot = zotero.Zotero(1892855,'group',config.zotero_api_key)

hacktag = ":enTitle seriesTitle"


tagzotitems = pyzot.items(tag=hacktag)
print('Found '+str(len(tagzotitems))+' items.')
# if len(tagzotitems) > 50:
# 	print('That is more than 50, abort.')
# 	sys.exit()

updatedzotitems = []
for zotitem in tagzotitems:
	if len(zotitem['data']['seriesTitle']) > 1:
		zotitem['data']['seriesTitle'] = ""
		if {'tag': hacktag} in zotitem['data']['tags']:
			print('Found hacktag and will remove it.')
			zotitem['data']['tags'].remove({'tag': hacktag})
		updatedzotitems.append(zotitem)

#print(str(updatedzotitems))

# update items
iterations = math.trunc((len(updatedzotitems) / 50) + 1)
actions = 0
while actions < iterations:
	listslice = updatedzotitems[actions*50:(actions+1)*50]
	#pyzot.update_items(listslice)
	actions += 1
	print('Successfully updated slice #'+str(actions)+'.')



# pyzot.delete_tags(hacktag)


# pyzot.add_tags(tagzotitem, ":container "+v3container)
# 	print('container-tag '+v3container+' written to '+tagzotitem['key'])
# 	time.sleep(0.2)
# pyzot.delete_tags(":container "+container)
# print('Zotero container tag '+container+' updated to '+v3container)
