#!/usr/share/python/

import csv

class School:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.games = set([])
        
    def __str__(self):
        return self.name
        
    def AddGame(self, g):
        self.games.add(g)
    
    def WinCount(self):
        count = 0;
        
        for g in self.games:
            if g.winner == self:
                count += 1
        
        return count
    
    def LossCount(self):
        count = 0;
        
        for g in self.games:
            if g.loser == self:
                count += 1
        
        return count
            
    def __eq__(self, other):
        return self.id == other.id

class Game:
    def __init__(self, home, away, hscore, ascore, date, neutral):
        self.home = home
        self.away = away
        self.hscore = int(hscore)
        self.ascore = int(ascore)
        self.date = date
        self.neutral = neutral
        
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
        output = self.winner.name + ' over ' + self.loser.name + ': ' + str(self.wscore) + ' - ' + str(self.lscore)
        
        if self.neutral:
            output += ' (Neutral field)'
        else:
            output += ' (At ' + self.home.name + ')'
        
        return output
    
    def __hash__(self):
        return hash(str(self))
    
    def __cmp__(self, other):
        if str(self) == str(other):
            return 0
        else:
            return 1
    
def AddGame(row):
    neutral = False

    if row['InstitutionID'] in allSchools:
        h = allSchools[row['InstitutionID']]
    else:
        h = School(row['InstitutionID'], row['Institution'])
        fbsSchools[h.id] = h
        allSchools[h.id] = h

    if row['Opponent ID'] in allSchools:
        a = allSchools[row['Opponent ID']]
    else:
        a = School(row['Opponent ID'], row['Opponent Name'])
        allSchools[h.id] = h
        
    if row['Location'] == 'Neutral Site':
        neutral = True

    if row['Location'] == 'Away':
        temp = h
        h = a
        a = temp
        hscore = row['Score Against']
        ascore = row['Score For']
    else:
        hscore = row['Score For']
        ascore = row['Score Against']
    
    g = Game(h, a, hscore, ascore, row['Game Date'], neutral)
    h.AddGame(g)
    a.AddGame(g)

fbsSchools = dict()
allSchools = dict()

reader = csv.DictReader(open('fbs.2010.final.csv', 'rb'), delimiter=',', quotechar='"')

for row in reader:
    AddGame(row)

for id, s in fbsSchools.iteritems():
    print str(s) + ' (' + str(s.WinCount()) + ' - ' + str(s.LossCount()) + ')'
    
    for g in s.games:
        print g
        
    print

