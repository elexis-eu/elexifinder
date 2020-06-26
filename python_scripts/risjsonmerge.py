# joins two RIS-JSON files, using one RIS key as Pivot, by dlindem
import json

pk = 'TI' # pivot key is AN
risjson_file_orig_items = 'D:/Lab_LexBib/eLexMerge/zotero.json'
risjson_file_new_items = 'D:/Lab_LexBib/eLexMerge/elexifinder.json'
new_items_not_found_in_orig ='D:/Lab_LexBib/eLexMerge/elexi_new.json'
merged_result = 'D:/Lab_LexBib/eLexMerge/mergedris.json'

with open(risjson_file_orig_items, encoding="utf-8") as f:
	original =  json.load(f, encoding="utf-8")
with open(risjson_file_new_items, encoding="utf-8") as f:
	newcomer =  json.load(f, encoding="utf-8")

mergecount = 0
for origitem in original:
	#print(origitem)
	#print(origitem['AN'])
	for newitem in newcomer:
		if pk in newitem and pk in origitem and str(origitem[pk]).lower() == str(newitem[pk]).lower(): #compares lower case version of PK value
			mergecount = mergecount + 1
			print('found merge candidate #'+str(mergecount))
			for key, value in origitem.items():
				if key != pk:
					try:
						origitem[key].extend(newitem[key])
					except KeyError:
						pass
			for key, value in newitem.items():
				if origitem.get(key) == None:
					origitem[key] = newitem[key]
			newcomer.remove(newitem) # after merging, delete item from newcomer json



with open(merged_result, 'w', encoding="utf-8") as json_file:
	json.dump(original, json_file, ensure_ascii=False, indent=2)
with open(new_items_not_found_in_orig, 'w', encoding="utf-8") as json_file:
	json.dump(newcomer, json_file, ensure_ascii=False, indent=2)
