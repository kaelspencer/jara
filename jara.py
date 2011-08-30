#!/usr/share/python/

import csv

reader = csv.DictReader(open('fbs.2010.final.csv', 'rb'), delimiter=',', quotechar='"')

for row in reader:
    print row['Institution'] + ' ' + row['Score For'] + ' VS ' + row['Opponent Name'] + ' ' + row['Score Against']

