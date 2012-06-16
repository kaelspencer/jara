#!/usr/share/python/

from datetime import date
import csv
import math

#
# A class to hold the ranking components for an individual team
#
class Rank:
    ranking = 0
    winPercent = 0
    winPercentWeight = 100
    winOver = 0
    winOverWeight = 150
    strengthOfSchedule = 0
    strengthOfScheduleWeight = 100
    
    def TotalPoints(self):
        total = self.winPercent * self.winPercentWeight
        total += self.winOver * self.winOverWeight
        total += self.strengthOfSchedule * self.strengthOfScheduleWeight
        
        return total
#
# A team object which holds a list of games
#
class Team:
    wincount = 0
    losscount = 0
    oppWinCount = 0
    oppLossCount = 0
    isFbs = False
    
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
    precision_digits = 1000; # Use three decimal places
    
    def __init__(self, teams):
        self.teams = teams
        self.totalTeams = float(len(self.teams))
        
    def Rank(self):
        # This has the side effect of giving all FBS teams a ranking.
        # After this, FCS schools will still have a ranking of 0.
        self.order = self.OrderByWinPer()
        self.UpdateRankings()
        
        self.DetermineStrenghOfSchedule()
        self.NormalizeStrengthOfSchedule()
        self.UpdateRankings()

        print self.GetRankingDisplay(25)
                
        for a in range(1, 50):
            self.OrderByWinOver()
            self.NormalizeWinOver()
            self.UpdateRankings()
            
        print self.GetRankingDisplay(25)
    
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
                
                output += str(rank).rjust(3) + '  ' + str(team).ljust(20) + ' Total points: ' + ('%.3f' % team.rank.TotalPoints())
                output += '\t(' + str(team.wincount).rjust(2) + ' - ' + str(team.losscount) + ')'
                output += '\t Win Over: ' + ('%.3f' % (team.rank.winOver * team.rank.winOverWeight)).rjust(7)
                output += '\t Win Per: ' + ('%.3f' % (team.rank.winPercent * team.rank.winPercentWeight)).rjust(6)
                output += '\t SoS: ' + ('%.3f' % (team.rank.strengthOfSchedule * team.rank.strengthOfScheduleWeight))
                output += ' (' + str(team.oppWinCount) + ' - ' + str(team.oppLossCount) + ', ' + ('%.3f' % team.rank.strengthOfSchedule) + ')'
                output += '\n'
        
        return output
    
    def OrderByWinPer(self):
        ordered = dict()
        retOrder = dict()
        
        for id in sorted(self.teams.keys()):
            team = self.teams[id]
            winPer = team.WinPercent()
            team.rank.winPercent = winPer
            
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

            pos -= len(ordered[winPer])
            retOrder[revPos] = posList
            revPos += len(ordered[winPer])
        
        return retOrder
    
    def OrderByWinOver(self):
        for id, team in self.teams.iteritems():
            points = 0
            
            for dt, game in team.games.iteritems():
                if game.winner == team:
                    points += self.DetermineGamePoints(game)
            
            team.rank.winOver = points
    
    def NormalizeWinOver(self):
        max = 0
        min = 101
        
        for id, team in self.teams.iteritems():
            if team.rank.winOver > max:
                max = team.rank.winOver
            
            if team.rank.winOver != 0 and team.rank.winOver < min:
                min = team.rank.winOver
        
        assert max > 0 and min > 0 and min < 101
        assert max - min > 0

        for id, team in self.teams.iteritems():
            team.rank.winOver = (team.rank.winOver - min) / (max - min)
    
    def DetermineStrenghOfSchedule(self):        
        for id, team in self.teams.iteritems():
            oppWins = 0
            oppLosses = 0
            
            for dt, game in team.games.iteritems():
                if game.winner == team:
                    oppTeam = game.loser
                else:
                    oppTeam  = game.winner
                
                # Only count FBS opponents.
                if oppTeam.isFbs:
                    oppWins += oppTeam.wincount
                    oppLosses += oppTeam.losscount
            
            # Some transitional teams (FCS -> FBS) teams will have 0 FBS opponents. Their SoS will be 0.
            if oppWins + oppLosses == 0:
                team.rank.strengthOfSchedule = 0
            else:
                team.rank.strengthOfSchedule = float(oppWins) / (oppWins + oppLosses)
            
            team.oppWinCount = oppWins
            team.oppLossCount = oppLosses
    
    def NormalizeStrengthOfSchedule(self):
        max = 0
        min = 101
        
        for id, team in self.teams.iteritems():
            if team.rank.strengthOfSchedule > max:
                max = team.rank.strengthOfSchedule
            
            if team.rank.strengthOfSchedule != 0 and team.rank.strengthOfSchedule < min:
                min = team.rank.strengthOfSchedule
        
        assert max > 0 and min > 0 and min < 101
        assert max - min > 0

        for id, team in self.teams.iteritems():
            team.rank.strengthOfSchedule = (team.rank.strengthOfSchedule - min) / (max - min)
    
    def DetermineGamePoints(self, game):
        bucketSize = 5
        numBuckets = math.ceil(self.totalTeams / bucketSize)
        
        # Only count points for wins over an FBS school.
        if game.loser.isFbs:
            gamepoints = numBuckets - math.floor(game.loser.rank.ranking / bucketSize)
        else:
            gamepoints = 0
            
        return gamepoints

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
            h.isFbs = True
    else:
        h = Team(row['Institution ID'], row['Institution'])
        fbsTeams[h.id] = h
        allTeams[h.id] = h
        h.isFbs = True

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
