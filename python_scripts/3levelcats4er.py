import re
import json
import os
import sys
from unidecode import unidecode


try:
    with open('D:/LexBib/terms/terms_languages_4er.json', encoding="utf-8") as f:
        subjdict =  json.load(f, encoding="utf-8")
except:
    print ('Error: input file does not exist.')
    sys.exit()

results = subjdict['results']
bindings = results['bindings']
#print(bindings)

ertermdic = {}
ertermlist = []

def wr_broaders(source):
#    print (str(source))
    er_uri_append = ""
    er_label_append = ""
    er_uri_append += '/'+bindings[source]['2nd_level_broader']['value'].replace('http://lexbib.org/terms#','').replace('http://lexvo.org/id/iso639-3/', 'Lang_')
    er_label_append += '/'+bindings[source]['2nd_level_broaderLabel']['value'].rstrip().title()
#    print(er_uri_append)
    if '3rd_level_broader' in bindings[source]:
        er_uri_append += '/'+bindings[source]['3rd_level_broader']['value'].replace('http://lexbib.org/terms#','').replace('http://lexvo.org/id/iso639-3/', 'Lang_')
        er_label_append += '/'+bindings[source]['3rd_level_broaderLabel']['value'].rstrip().title()


    return [er_uri_append, er_label_append]


for item in range(len(bindings)):
#    print(str(item))

    subjectLabelNorm = unidecode(bindings[item]['subjectLabel']['value']).lower().rstrip()
    subjectLabelNorm = re.sub(r'[ \-\']','_',subjectLabelNorm)
    subjectLabelNorm = re.sub(r'__+','_',subjectLabelNorm)


    if '2nd_level_broader' in bindings[item]:
        itemdict = {'subject_uri':bindings[item]['subject']['value'],'subjectLabel':bindings[item]['subjectLabel']['value'].rstrip(),'er_uri':'Term_Lexicography','er_label':'Lexicography'}
    #    print(str(item))
        addbroad = wr_broaders(item)
    #    print(addbroad)
        itemdict['er_uri'] += addbroad[0]
        itemdict['er_label'] += addbroad[1]

        itemdict['er_uri'] += '/'+bindings[item]['subject']['value'].replace('http://lexbib.org/terms#','').replace('http://lexvo.org/id/iso639-3/', 'Lang_')
        itemdict['er_label'] += '/'+bindings[item]['subjectLabel']['value'].rstrip().title()

        # else:
        #     itemdict['er_uri'] += '/'+item['subject']['value'].replace('http://lexbib.org/terms#','').replace('http://lexvo.org/id/iso639-3/', 'Lang_')
        #     itemdict['er_label'] += '/'+item['subjectLabel']['value'].rstrip().title()
        #     item += 1
    elif '2nd_level_broader' not in bindings[item]:
        if 'synonym' not in bindings[item]:
            print('Found orphaned term '+subjectLabelNorm)
            continue
            #print(bindings[item]['synonym'])
        else:
            for binding in range(len(bindings)):
                #print (binding['subject']['value'])
                if bindings[binding]['subject']['value'] == bindings[item]['synonym']['value']:
                    #print('hallo synonym')
                    if '2nd_level_broader' in bindings[binding]:
                        itemdict = {'subject_uri':bindings[item]['subject']['value'],'subjectLabel':bindings[item]['subjectLabel']['value'].rstrip(),'er_uri':'Term_Lexicography','er_label':'Lexicography'}
                        addbroad = wr_broaders(binding)
                        itemdict['er_uri'] += addbroad[0]
                        itemdict['er_label'] += addbroad[1]

                        itemdict['er_uri'] += '/'+bindings[item]['subject']['value'].replace('http://lexbib.org/terms#','').replace('http://lexvo.org/id/iso639-3/', 'Lang_')
                        itemdict['er_label'] += '/'+bindings[item]['subjectLabel']['value'].rstrip().title()



    # if '4th_level_broader' in item:
    #     itemdict['er_uri'] += item['4th_level_broader']['value'].replace('http://lexbib.org/terms#','')+'/'
    #     itemdict['er_label'] += item['4th_level_broaderLabel']['value'].rstrip()+'/'
    #

    #append subject label
    #itemdict['er_label'] += item['subjectLabel']['value'].rstrip()
    #itemdict['er_uri'] += item['subject']['value'].replace('http://lexbib.org/terms#','')


    ertermlist.append(itemdict)

    if subjectLabelNorm not in ertermdic:
        ertermdic[subjectLabelNorm] = [itemdict]
    else:
        ertermdic[subjectLabelNorm].append(itemdict)



with open('D:/LexBib/terms/er_skos_3levelcats_dic.json', 'w', encoding="utf-8") as json_file:
	json.dump(ertermdic, json_file, indent=2)
with open('D:/LexBib/terms/er_skos_3levelcats_list.json', 'w', encoding="utf-8") as json_file:
	json.dump(ertermlist, json_file, indent=2)
