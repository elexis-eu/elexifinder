import re
import json
import os
import sys
from unidecode import unidecode


try:
    with open('D:/LexBib/terms/4_level_terms.json', encoding="utf-8") as f:
        subjdict =  json.load(f, encoding="utf-8")
except:
    print ('Error: file "5_level_terms.json" does not exist.')
    sys.exit()

results = subjdict['results']
bindings = results['bindings']
print(bindings)

ertermdic = {}
ertermlist = []
for item in bindings:

    subjectLabelNorm = unidecode(item['subjectLabel']['value']).lower().rstrip()
    subjectLabelNorm = re.sub(r'[ \-\']','_',subjectLabelNorm)
    subjectLabelNorm = re.sub(r'__+','_',subjectLabelNorm)

    itemdict = {'subject_uri':item['subject']['value'],'subjectLabel':item['subjectLabel']['value'].rstrip(),'er_uri':'Term_Lexicography/','er_label':'Lexicography/'}
    if '2nd_level_broader' in item:
        itemdict['er_uri'] += item['2nd_level_broader']['value'].replace('http://lexbib.org/terms#','')+'/'
        itemdict['er_label'] += item['2nd_level_broaderLabel']['value'].rstrip()+'/'
    if '3rd_level_broader' in item:
        itemdict['er_uri'] += item['3rd_level_broader']['value'].replace('http://lexbib.org/terms#','')+'/'
        itemdict['er_label'] += item['3rd_level_broaderLabel']['value'].rstrip()+'/'
    if '4th_level_broader' in item:
        itemdict['er_uri'] += item['4th_level_broader']['value'].replace('http://lexbib.org/terms#','')+'/'
        itemdict['er_label'] += item['4th_level_broaderLabel']['value'].rstrip()+'/'
    itemdict['er_uri'] += item['subject']['value'].replace('http://lexbib.org/terms#','')
    itemdict['er_label'] += item['subjectLabel']['value'].rstrip()

    ertermlist.append(itemdict)

    if subjectLabelNorm not in ertermdic:
        ertermdic[subjectLabelNorm] = [itemdict]
    else:
        ertermdic[subjectLabelNorm].append(itemdict)

with open('D:/LexBib/terms/er_skos_4levels_dic.json', 'w', encoding="utf-8") as json_file:
	json.dump(ertermdic, json_file, indent=2)
with open('D:/LexBib/terms/er_skos_4levels_list.json', 'w', encoding="utf-8") as json_file:
	json.dump(ertermlist, json_file, indent=2)
