#!/usr/share/python/

from datetime import date
import csv
import math

#
# A class to hold the ranking components for an individual team
#
class Rank:
    ranking = 124
    winPercent = 0
    winPercentWeight = 0.001
    winOver = 0
    winOverWeight = 1
    
    def TotalPoints(self):
        total = self.winPercent * self.winPercentWeight
        total += self.winOver * self.winOverWeight
        
        return total

#
# A team object which holds a list of games
#
class Team:
    wincount = 0
    losscount = 0
    
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.games = dict()
        self.rank = Rank()
        
    def __str__(self):
        return self.name
        
    def AddGame(self, g):
        if not g.date in self.games:
            self.games[g.date] = g
            
            if g.winner == self:
                self.wincount += 1
            else:
                self.losscount += 1
    
    def WinPercent(self):
        return float(self.wincount) / (self.wincount + self.losscount)
    
    def __eq__(self, other):
        return self.id == other.id

#
# Information about a single game
#
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

#
# Holds the ranking order of all teams
#
class Ranking:
    order = dict()
    precision_digits = 1000; #U se three decimal places
    
    def __init__(self, teams):
        self.teams = teams
        self.totalTeams = float(len(self.teams))
        
    def Rank(self):
        self.order = self.OrderByWinPer()
        self.UpdateRankings()
        
        print self.GetRankingDisplay(10)
        
        for a in range(1, 5):
            for b in range(1, 5):
                self.OrderByWinOver(10)
                self.UpdateRankings()
            print self.GetRankingDisplay(10)
    
    def UpdateRankings(self):
        preorder = dict()
        self.order = dict()
        
        for id, team in self.teams.iteritems():
            tp = round(team.rank.TotalPoints() * self.precision_digits)
            
            if tp in preorder.keys():
                preorder[tp].append(team)
            else:
                preorder[tp] = [team]
        
        revPos = 1
        
        for points in sorted(preorder.keys(), reverse=True):
            posList = list()
            
            for team in preorder[points]:
                posList.append(team)

            self.order[revPos] = posList
            revPos += len(preorder[points])
        
        for rank, teams in self.order.iteritems():
            for team in teams:
                team.rank.ranking = rank
    
    def GetRankingDisplay(self, count = 0):
        output = ''
        i = 0
        
        for rank in sorted(self.order.keys()):
            for team in self.order[rank]:
                if count != 0 and i >= count:
                    break
                
                i += 1
                
                output += str(rank).rjust(3) + '  ' + str(team).ljust(20) + ' Total points: ' + ('%.3f' % (team.rank.TotalPoints(),))
                output += '\t(' + str(team.wincount) + ' - ' + str(team.losscount) + ')\n'
        
        return output
    
    def OrderByWinPer(self):
        ordered = dict()
        retOrder = dict()
        
        for id in sorted(self.teams.keys()):
            team = self.teams[id]
            winPer = team.WinPercent()
            
            if winPer in ordered.keys():
                ordered[winPer].append(team)
            else:
                ordered[winPer] = [team]
        
        revPos = 1
        pos = self.totalTeams
        
        for winPer in sorted(ordered.keys(), reverse=True):
            posList = list()
            
            for team in ordered[winPer]:
                posList.append(team)
                team.rank.winPercent = round(pos / self.totalTeams * 1000)

            pos -= len(ordered[winPer])
            retOrder[revPos] = posList
            revPos += len(ordered[winPer])
        
        return retOrder
    
    def OrderByWinOver(self, bucketSize):
        numBuckets = math.ceil(self.totalTeams / bucketSize)
        maxPoints = 0
        
        for id, team in self.teams.iteritems():
            points = 0
            
            #print team.name + ': '
            for dt, game in team.games.iteritems():
                if game.winner == team:
                    gamepoints = numBuckets - math.floor(game.loser.rank.ranking / bucketSize) 
                    points += gamepoints
                    #print '\tBeat ' + str(game.loser.rank.ranking).rjust(3) + ' ' + game.loser.name.ljust(20) + 'Points: ' + str(gamepoints)
            
            #points /= len(team.games.keys())
            team.rank.winOver = points
            #print team.name.ljust(20) + ' ' + str(team.rank.winOver).rjust(8)
            #print
            
            if points > maxPoints:
                maxPoints = points
        
        for id, team in self.teams.iteritems():
            team.rank.winOver /= float(maxPoints)

#
# Parses a row of the CSV file, creates games and teams as needed
#
def AddGame(row, fbsTeams, allTeams):
    neutral = False

    if row['Institution ID'] in allTeams:
        h = allTeams[row['Institution ID']]
        
        # Hey, this team showed up in the left column! They're an FBS team.
        if row['Institution ID'] not in fbsTeams:
            fbsTeams[h.id] = h
    else:
        h = Team(row['Institution ID'], row['Institution'])
        fbsTeams[h.id] = h
        allTeams[h.id] = h

    if row['Opponent ID'] in allTeams:
        a = allTeams[row['Opponent ID']]
    else:
        a = Team(row['Opponent ID'], row['Opponent Name'])
        allTeams[a.id] = a
        
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

#
# Prints all teams and their game results
#
def PrintAllTeams(fbsTeams):
    for id in sorted(fbsTeams.keys()):
        team = fbsTeams[id]
        print str(team.rank.ranking).rjust(3) + ' ' + str(team) + ' (' + str(team.wincount) + ' - ' + str(team.losscount) + ') '
        
        for date in sorted(team.games.keys()):
            print team.games[date].Pretty(team)
        
        print

#
# Main
#
fbsTeamList = dict()
allTeamList = dict()

reader = csv.DictReader(open('fbs.2011.final.csv', 'rb'), delimiter=',', quotechar='"')

for row in reader:
    AddGame(row, fbsTeamList, allTeamList)

rank = Ranking(fbsTeamList)
rank.Rank()
#print rank.GetRankingDisplay(10)

#PrintAllTeams(fbsTeamList)
