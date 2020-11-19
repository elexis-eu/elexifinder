import json, time, re


with open('D:/LexBib/groupsources/query-result.srj', 'r', encoding="utf-8") as infile:
    colldict = json.load(infile, encoding="utf-8")['results']['bindings']
    print(str(colldict))
result = {}
result['sourceGroupToList'] = {}
useduri = []
for item in colldict:

    coll = item['coll']['value']

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
        sourcestring = title + ' <' + source + '>'
        if 'general/'+coll not in result['sourceGroupToList']:
            result['sourceGroupToList']['general/'+coll]=[sourcestring]
            useduri.append(source)
        else:
            if sourcestring not in result['sourceGroupToList']['general/'+coll]:
                result['sourceGroupToList']['general/'+coll].append(sourcestring)
                useduri.append(source)

with open('D:/LexBib/groupsources/grouped_sources.json', 'w', encoding="utf-8") as outfile:
    json.dump(result['sourceGroupToList'], outfile, ensure_ascii=False, indent=2)

collnames = {
1 : 'eLex Conferences',
2 : 'EURALEX Conferences',
3 : 'International Journal of Lexicography',
4 : 'Lexikos',
5 : 'LexicoNordica',
6 : 'Lexicographica',
7 : 'Nordiske Studier i Leksikografi',
8 : 'Lexicon Tokyo',
9 : 'Lexicography Journal of Asialex',
10 : 'Globalex'
}

result['sourceGroupUriName'] = {}
for coll in result['sourceGroupToList']:

    result['sourceGroupUriName'][coll] = 'General/'+collnames[int(re.search('/(\d+)', coll).group(1))]

with open('D:/LexBib/groupsources/result.json', 'w', encoding="utf-8") as outfile:
    json.dump(result, outfile, ensure_ascii=False, indent=2)
