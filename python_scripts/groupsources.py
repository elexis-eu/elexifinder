import json, time, re

zotero_collections = {
1 : {"name" : "eLex Conferences", "group": 1},
2 : {"name" : "EURALEX Conferences", "group": 1},
3 : {"name" : "International Journal of Lexicography", "group": 2},
4 : {"name" : "Lexikos", "group": 2},
5 : {"name" : "LexicoNordica", "group": 2},
6 : {"name" : "Lexicographica", "group": 2},
7 : {"name" : "Nordiske Studier i Leksikografi", "group": 2},
8 : {"name" : "Lexicon Tokyo", "group": 2},
9 : {"name" : "Lexicography Journal of Asialex", "group": 2},
10 : {"name" : "Globalex", "group": 1},
11 : {"name" : "Videos", "group": 3},
12 : {"name" : "Dictionaries (HSK 5/4)", "group": 5},
13 : {"name" : "Teubert (ed. 2007)", "group": 4},
14 : {"name" : "Fuertes Olivera (ed. 2010)", "group": 4},
15 : {"name" : "Müller-Spitzer (2014)", "group": 4},
16 : {"name" : "Slovenščina 2.0", "group": 2},
17 : {"name" : "Revista de Lexicografía", "group": 2},
18 : {"name" : "Bloomsbury Companion (2013)", "group": 5},
19 : {"name" : "Braun et al. (ed. 2003)", "group": 4},
20 : {"name" : "Lexicographica Series Maior 147 (2014)", "group": 4},
21 : {"name" : "Lexicografía Lenguas Románicas (2014)", "group": 4},
22 : {"name" : "Gottlieb & Morgensen (ed. 2007)", "group": 4},
23 : {"name" : "Wiegand (ed. 2000)", "group": 4},
24 : {"name" : "Wiegand (ed. 2003)", "group": 4},
25 : {"name" : "Sterkenburg (ed. 2003)", "group": 5},
}

er_groupnames = {
1 : "Proceedings",
2 : "Journals",
3 : "Videos",
4 : "Book Chapters",
5 : "Handbook Chapters"
}


# this takes sparql query result (json-ld) from 'rdf2er/groupsquery.rq'
with open('D:/LexBib/groupsources/query-result.srj', 'r', encoding="utf-8") as infile:
    colldict = json.load(infile, encoding="utf-8")['results']['bindings']
    print(str(colldict))
result = {}
result['sourceGroupToList'] = {}
useduri = []
for item in colldict:
    zotcoll = int(item['coll']['value'])
    zotcollname = zotero_collections[zotcoll]['name']
    ercoll = zotero_collections[zotcoll]['group']
    ercollname = er_groupnames[ercoll]

    if 'containerFullTextUrl' in item:
        source = item['containerFullTextUrl']['value']
    else:
        if 'containerUri' in item:
            source = item['containerUri']['value']
        else:
            source = ""
    if 'containerShortTitle' in item:
        title = item['containerShortTitle']['value']
    else:
        title = re.sub(r'https?://', '', source)

    if source != "" and source not in useduri:
        sourcestring = source #title + ' <' + source + '>' // change: title is not wanted here
        if 'general/'+str(ercoll) not in result['sourceGroupToList']:
            result['sourceGroupToList']['general/'+str(ercoll)]=[sourcestring]
            useduri.append(source)
        else:
            if sourcestring not in result['sourceGroupToList']['general/'+str(ercoll)]:
                result['sourceGroupToList']['general/'+str(ercoll)].append(sourcestring)
                useduri.append(source)

with open('D:/LexBib/groupsources/grouped_sources.json', 'w', encoding="utf-8") as outfile:
    json.dump(result['sourceGroupToList'], outfile, ensure_ascii=False, indent=2)



result['sourceGroupToName'] = {}
for coll in result['sourceGroupToList']:
    ercollkey = int(coll.split('/')[1])
    result['sourceGroupToName'][coll] = 'General/'+er_groupnames[ercollkey]

with open('D:/GitHub/elexifinder/rdf2er/elexifinder_groups.json', 'w', encoding="utf-8") as outfile:
    json.dump(result, outfile, ensure_ascii=False, indent=2)
