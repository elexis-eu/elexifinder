import re
import json
import time

ris_input_file = 'D:/Lab_LexBib/Lexicographica/LEXICOGRAPHICA_doidisambig/LEXICOGRAPHICA_doidisambig.ris'
ris_output_file = 'D:/Lab_LexBib/Lexicographica/LEXICOGRAPHICA_doidisambig/LEXICOGRAPHICA_doidisambiguated.ris'

with open(ris_input_file, 'r', encoding="utf-8") as risfile:
    ris = risfile.read().split('\n')

repcount = 1
newris = ""
useddoi = []
for line in ris:
    #print(line)
    doiline = re.search('^DO  - (.*)', line)
    if doiline != None:
        doi = doiline.group(1)
        print('orig doi: '+doi)
        if doi in useddoi:
            print('\ndouble doi: '+doi)
            newdoi = doi.replace('/','_')+"_"+str(repcount)
            print('new doi with disambiguator: '+newdoi+'\n')
            repcount += 1
            newris += "AN  - "+newdoi+"\n" # use item uri with disambiguator but in lexbib item namespace, not as doi
            #time.sleep(1)
        else:
            newris += "AN  - doi:"+doi+"\n"
            useddoi.append(doi)
    newris += line+"\n"

with open(ris_output_file, 'w', encoding="utf-8") as risfile:
    risfile.write(newris)
