#!/usr/share/python/

import csv

class School:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.games = []
        
    def __str__(self):
        return self.name + ' (' + self.id + ')'
        
    def AddGame(self, g):
        self.games.append(g)

class Game:
    def __init__(self, home, away, hscore, ascore, date):
        self.home = home
        self.away = away
        self.hscore = hscore
        self.ascore = ascore
        self.date = date
        
        if self.hscore > self.ascore:
            self.winner = self.home
            self.loser = self.away
            self.wscore = self.hscore
            self.lscore = self.ascore
        else:
            self.winner = self.away
            self.loser = self.home
            self.wscore = self.ascore
            self.lscore = self.hscore
    
    def __str__(self):
        return self.winner.name + ' over ' + self.loser.name + ': ' + self.wscore + ' - ' + self.lscore
    
def AddGame(row):
    if row['InstitutionID'] in schools:
        h = schools[row['InstitutionID']]
    else:
        h = School(row['InstitutionID'], row['Institution'])
        schools[h.id] = h

    if row['Opponent ID'] in schools:
        a = schools[row['Opponent ID']]
    else:
        a = School(row['Opponent ID'], row['Opponent Name'])
        schools[a.id] = a

    if row['Location'] == 'Away':
        temp = h
        h = a
        a = temp
        hscore = row['Score Against']
        ascore = row['Score For']
    else:
        hscore = row['Score For']
        ascore = row['Score Against']
    
    g = Game(h, a, hscore, ascore, row['Game Date'])
    h.AddGame(g)
    a.AddGame(g)

schools = dict()

reader = csv.DictReader(open('fbs.2010.final.csv', 'rb'), delimiter=',', quotechar='"')

for row in reader:
    AddGame(row)

for id, s in schools.iteritems():
    print s
    
    for g in s.games:
        print g
        
    print

