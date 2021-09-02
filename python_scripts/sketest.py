#!/usr/bin/python
import json
import requests
import time

with open('D:/LexBib/SkE/pwd.txt', 'r', encoding='utf-8') as pwdfile:
	pwd = pwdfile.read()

auth = ('jsi_api', pwd)
URL = 'https://api.sketchengine.eu/ca/api'
while True:
    r = requests.post(URL + '/corpora', auth=auth, json={
        'language_id': 'en',
        'name': 'LexBib/Elexifinder v8 English'
    })
    if "201" in str(r):
        print('Corpus created.')
        break

corpus_id = r.json()['data']['id']
corpus_url = URL + '/corpora/' + str(corpus_id)
corpname = r.json()['data']['corpname']
print('Corpus ID: '+str(corpus_id)+'\nCorpus URL: '+corpus_url+'\nCorpus name: '+corpname)

files = {'file': ('ABCDEFG/test_text.txt', open('D:/LexBib/SkE/testing.txt', 'rb'), 'text/plain')}
while True:
    r = requests.post(corpus_url + '/documents', auth=auth, files=files, params={'feeling': 'lucky'})
    if "201" in str(r):
        print('File(s) uploaded to corpus.')
        break
    time.sleep(1)

while True:
    print('Waiting for new corpus to be processed...')

    r = requests.post(corpus_url + '/can_be_compiled', json={}, auth=auth)
    if r.json()['result']['can_be_compiled']:
        break
	time.sleep(1)

while True:
    r = requests.post(corpus_url + '/compile', json={'structures': 'all'}, auth=auth)

    if "200" in str(r):
        print('Corpus compilation successfully triggered.')
        break
	time.sleep(1)

print ('Success.')
