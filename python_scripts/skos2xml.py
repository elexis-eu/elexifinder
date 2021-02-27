import xml.etree.ElementTree as xml
from xml.dom import minidom
import json

with open('D:/LexBib/terms/er_skos_3levelcats_dic.json', encoding="utf-8") as f:
    subjdict =  json.load(f, encoding="utf-8")

root = xml.Element('a3iadrmk')
for subj in subjdict:
	# filter non-valid term uri (TBD)
	for s in subjdict[subj]:
		entry = xml.Element('entry')
		root.append(entry)
		entry.set('lexbib_id',s['subject_uri'])
		term = xml.SubElement(entry, 'term')
		term_eng = xml.SubElement(term, 'term_eng')
		label_eng = xml.SubElement(term_eng, 'label_eng')
		label_eng.text = s['subjectLabel']
		translations = xml.SubElement(entry, 'translations')




tree_obj = xml.ElementTree(root)
with open('tree.xml', "w", encoding='utf-8') as file:
	reparsed = minidom.parseString(xml.tostring(root, 'utf-8')).toprettyxml(indent = "\t")
	print(reparsed)
	file.write(reparsed)
