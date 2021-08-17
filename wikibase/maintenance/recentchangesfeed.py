import requests
import xml.etree.ElementTree as ET
import lxml
import time

since = "2021-08-01T00%3A00%3A00.000Z"

queryurl = "https://data.lexbib.org/w/api.php?action=feedrecentchanges&format=json&feedformat=rss&hidebots=1&namespace=120&from="+since
done = False
while (not done):
	try:
		r = requests.get(queryurl)
		feed = ET.fromstring(str(r.content.decode("utf-8")))
	except Exception as ex:
		print('Error: SPARQL request failed: '+str(ex))
		time.sleep(2)
		continue
	done = True
#print(str(bindings))

print('Found rss feed of items changed since '+since+': \n')

channel = feed.find('channel')
items = channel.findall('item')
qidlist = []
for item in items:
	title = item.find('title').text.replace("Item:","")
	qidlist.append(title)
