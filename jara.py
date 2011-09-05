#!/usr/share/python/

from datetime import date
import csv

class Team:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.games = dict()
        
    def __str__(self):
        return self.name
        
    def AddGame(self, g):
        if not g.date in self.games:
            self.games[g.date] = g
    
    def WinCount(self):
        count = 0;
        
        for d, g in self.games.iteritems():
            if g.winner == self:
                count += 1
        
        return count
    
    def LossCount(self):
        count = 0;
        
        for d, g in self.games.iteritems():
            if g.loser == self:
                count += 1
        
        return count
            
    def __eq__(self, other):
        return self.id == other.id

class Game:
    def __init__(self, home, away, hscore, ascore, date, neutral):
        self.home = home
        self.away = away
        self.hscore = hscore
        self.ascore = ascore
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
    
    def Pretty(self, team):
        output = str(self.date) + '\t'
        
        if self.away == team:
            output += 'at ' + str(self.home)
        else:
            output += 'vs ' + str(self.away)
        
        output = output.ljust(35)
        
        if self.winner == team:
            output += 'W'
        else:
            output += 'L'
        
        output += '  ' + str(self.wscore).rjust(2) + ' - ' + str(self.lscore).rjust(2)
        
        if self.neutral:
            output += '\t(Neutral field)'
        
        return output
    
    def __str__(self):
        teams = self.winner.name + ' over ' + self.loser.name
        output = str(self.date) + '\t' + teams.ljust(40) + str(self.wscore).rjust(2) + ' - ' + str(self.lscore).rjust(2)
        
        if self.neutral:
            output += '\t\t(Neutral field)'
        else:
            output += '\t\t(At ' + self.home.name + ')'
        
        return output
    
    def __cmp__(self, other):
        if str(self) == str(other):
            return 0
        else:
            return 1
    
def AddGame(row):
    neutral = False

    if row['InstitutionID'] in allTeams:
        h = allTeams[row['InstitutionID']]
    else:
        h = Team(row['InstitutionID'], row['Institution'])
        fbsTeams[h.id] = h
        allTeams[h.id] = h

    if row['Opponent ID'] in allTeams:
        a = allTeams[row['Opponent ID']]
    else:
        a = Team(row['Opponent ID'], row['Opponent Name'])
        allTeams[h.id] = h
        
    if row['Location'] == 'Neutral Site':
        neutral = True

    if row['Location'] == 'Away':
        temp = h
        h = a
        a = temp
        hscore = int(row['Score Against'])
        ascore = int(row['Score For'])
    else:
        hscore = int(row['Score For'])
        ascore = int(row['Score Against'])
    
    dateSubparts = row['Game Date'].split('/') # Format: MM/DD/YY
    # BUG: Reverse Y2K bug? Yes. Fix.
    d = date(2000 + int(dateSubparts[2]), int(dateSubparts[0]), int(dateSubparts[1]))
    
    g = Game(h, a, hscore, ascore, d, neutral)
    h.AddGame(g)
    a.AddGame(g)

def PrintAllTeams():
    for id in sorted(fbsTeams.keys()):
        team = fbsTeams[id]
        print str(team) + ' (' + str(team.WinCount()) + ' - ' + str(team.LossCount()) + ')'
        
        for date in sorted(team.games.keys()):
            print team.games[date].Pretty(team)
        
        print

fbsTeams = dict()
allTeams = dict()

reader = csv.DictReader(open('fbs.2010.final.csv', 'rb'), delimiter=',', quotechar='"')

for row in reader:
    AddGame(row)

PrintAllTeams()
