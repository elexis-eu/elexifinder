import sys, re, time, requests, json, os
import wikify


wikiterms = {}

with open('D:/LexBib/bodytxt/bodytxt_collection.json', encoding="utf-8") as jsonfile:
	bodytxts = json.load(jsonfile)

resultdir = os.listdir('D:/LexBib/bodytxt/wikification')

# with open('D:/LexBib/bodytxt/foundterms_last.json', encoding="utf-8") as jsonfile:
# 	foundterms = json.load(jsonfile)

count = 0
wikicount = 0
total = str(len(bodytxts))
wikipagelabels = {}
for bibitem in bodytxts:
	count += 1
	if bibitem+".json" in resultdir:
		continue
		# with open('D:/LexBib/bodytxt/wikification/'+bibitem+'.json', 'r', encoding="utf-8") as jsonfile:
		# 	itemterms = json.load(jsonfile)
		# if itemterms['concepts'] != None:
		# 	print('Result already there, will skip wikification for '+bibitem)
		# else:
		# 	itemterms = wikify.wikify(bibitem, bodytxts[bibitem]['bodytxt'])
		# 	print(str(count)+' of '+total+': Successfully wikified bibitem '+bibitem+' (not succesfully in previous runs)')
		# 	time.sleep(0.2)
	else:
		itemterms = wikify.wikify(bibitem, bodytxts[bibitem]['bodytxt'])
		wikicount += 1
		print(str(count)+' of '+total+': Successfully wikified bibitem '+bibitem+'. Wikifications in this run: '+str(wikicount)+'.')
		time.sleep(0.2)
	wikiterms[bibitem] = itemterms

	if itemterms['concepts']:
		for term in itemterms['concepts']:
			if term['uri'] not in wikipagelabels:
				wikipagelabels[term['uri']] = {'label': term['label'], 'count': 1}
			else:
				wikipagelabels[term['uri']]['count'] += 1


with open('D:/LexBib/bodytxt/foundwikiterms.json', "w", encoding="utf-8") as jsonfile:
	json.dump(wikiterms, jsonfile, indent = 2)
with open('D:/LexBib/bodytxt/foundwikiterms_wikipagelabels.json', "w", encoding="utf-8") as jsonfile:
	json.dump(wikipagelabels, jsonfile, indent = 2)

print('\nFinished.')
