import config
import lwb
import csv

with open(config.datafolder+'containers/lexbiblegacycontainers.csv', 'r', encoding="utf-8") as csvfile:
	containers = csv.DictReader(csvfile)
	index = 0
	for container in containers:
		index += 1

		print('\n['+str(index)+'] '+str(container)+'\n')
		legacyclasses = container['classes'].split(' ')
		print('Old classes: '+str(legacyclasses))
		classes = []
		for legacyclass in legacyclasses:
			newclass = lwb.getidfromlegid("Q2", legacyclass, onlyknown=True)
			if newclass == False:
				print('Error: No Qid for legacy class '+legacyclass)
			else:
				classes.append(newclass)
		print('New classes: '+str(classes))
		qid = lwb.newitemwithlabel(classes, "en", container['label'])
		statement = lwb.stringclaim(qid, "P1", container['containing_item'])
