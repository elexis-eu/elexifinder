# converts RIS into JSON, by dlindem
import re
import json

ris_input_file = 'D:/Lab_LexBib/BibMerge/VIDEOS.ris'
json_output_file = 'D:/Lab_LexBib/BibMerge/videos_old.json'

with open(ris_input_file, 'r', encoding="utf-8") as risfile:
    ris = risfile.read()

risjson = []
risobjects = ris.split('\nER  - \n')
for risobject in risobjects:
    risdict = {}
    # notrisline = "^[^A-Z]{2}  \- "
    risobject = re.sub(r"([A-Z][A-Z1-4]  \- )", r"@@@\1", risobject)
    risobject = re.sub(r"^@@@", "", risobject)
    #risobject = re.sub(r'\n', '\r\n', risobject)
    #risobject = re.sub("\n@@@", "@@@", risobject)
    rislines = risobject.split('\n@@@')
    for risline in rislines:
        try:
            splitline = risline.split('  - ',1)
            riskey = splitline[0]
            risvalue = splitline[1]
            if riskey in risdict:
                risdict[riskey].append(risvalue)
            else:
                risdict[riskey] = [risvalue]
        except IndexError:
            pass

    risjson.append(risdict)
print(risjson)

with open(json_output_file, 'w', encoding="utf-8") as json_file:
	json.dump(risjson, json_file, ensure_ascii=False, indent=2)
