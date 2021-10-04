# converts CSV into JSON (keys in first csv row), by dlindem
import re
import json
import csv

with open('D:/Lab_LexBib/elex-2021/procs.csv', encoding="utf-8") as csvfile: # source file
    csvrows = csv.reader(csvfile, delimiter=",")
    csvkeys = next(csvrows)
    print(csvkeys)
    csvjson = []
    for row in csvrows:
        itemdict = {}
        print(str(row))
        for col in range(len(row)):
            if row[col] != "":
                if csvkeys[col] not in itemdict:
                    itemdict[csvkeys[col]] = [row[col]]
                else:
                    itemdict[csvkeys[col]].append(row[col])



        csvjson.append(itemdict)
print(csvjson)

with open('D:/Lab_LexBib/elex-2021/procs.json', 'w', encoding="utf-8") as json_file: # result file
	json.dump(csvjson, json_file, ensure_ascii=False, indent=2)
