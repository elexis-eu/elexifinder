# converts CSV into JSON (keys in first csv row), by dlindem
import re
import json
import csv

with open('D:/Lab_LexBib/eLexMerge/eLex-elexifinder.csv', encoding="utf-8") as csvfile: # source file
    csvdict = csv.DictReader(csvfile, delimiter="\t")
    csvjson = []
    for itemdict in csvdict:
        for riskey in itemdict:
            itemdict[riskey] = [itemdict[riskey]]
        csvjson.append(itemdict)
print(csvjson)

with open('D:/Lab_LexBib/eLexMerge/elexifinder.json', 'w', encoding="utf-8") as json_file: # result file
	json.dump(csvjson, json_file, ensure_ascii=False, indent=2)
