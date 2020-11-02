import re
import json
import os
import sys


try:
    with open('D:/LexBib/rdf2json/subjects_skos.json', encoding="utf-8") as f:
        subjdict =  json.load(f, encoding="utf-8")
except:
    print ('Error: file "subjects_skos.json" does not exist.')
    sys.exit()

results = subjdict['results']
bindings = results['bindings']
print(bindings)

keyextractlist = []
erkeyintlist = []

for item in bindings:
    #print(item['subject']['value']+item['subjectLabel']['value'])
    keyextractlist.append({'uri':item['subject']['value'] , 'label':item['subjectLabel']['value']})
    erkeyintlist.append({'subject_uri':item['subject']['value'], 'broaderslist':item['broaders']['value'], 'broaderlabelslist':item['broaderLabels']['value']})

#print(erkeylist)
erkeylist = []

for term in erkeyintlist:
    broaderslist = term['broaderslist'].split("@")
    broaderslist.reverse()
    er_uri = ''
    for broader in broaderslist:
        if broader != '':
            if er_uri == '':
                er_uri = re.search(r'[^/\#]+$', broader.replace('iso639-3/', 'iso639-3_')).group(0)
            else:
                er_uri += '/'+re.search(r'[^/\#]+$', broader.replace('iso639-3/', 'iso639-3_')).group(0)
    broaderlabelslist = term['broaderlabelslist'].split('@')
    broaderlabelslist.reverse()
    er_label = ''
    for broaderlabel in broaderlabelslist:
        if broaderlabel != '':
            if er_label == '':
                er_label = broaderlabel
            else:
                er_label += '/'+broaderlabel
    print(er_uri+' '+er_label)
    erkeylist.append({'subject_uri':term['subject_uri'], 'er_uri':er_uri, 'er_label':er_label})

with open('D:/LexBib/rdf2json/erkeys.json', 'w', encoding="utf-8") as json_file:
	json.dump(erkeylist, json_file, indent=2)
with open('D:/LexBib/rdf2json/keyextractlist.json', 'w', encoding="utf-8") as json_file:
	json.dump(keyextractlist, json_file, indent=2)
