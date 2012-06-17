#!/usr/share/python/

from datetime import date
import csv
import math

#
# A class to hold the ranking components for an individual team
#
class Rank:
    ranking = 0
    win_percent = 0
    win_percent_weight = 100
    win_over = 0
    win_over_weight = 150
    strength_of_schedule = 0
    strength_of_schedule_weight = 100
    
    def total_points(self):
        total = self.win_percent * self.win_percent_weight
        total += self.win_over * self.win_over_weight
        total += self.strength_of_schedule * self.strength_of_schedule_weight
        
        return total
#
# A team object which holds a list of games
#
class Team:
    win_count = 0
    loss_count = 0
    opp_win_count = 0
    opp_loss_count = 0
    is_fbs = False
    
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.games = dict()
        self.rank = Rank()
        
    def __str__(self):
        return self.name
        
    def add_game(self, g):
        if not g.date in self.games:
            self.games[g.date] = g
            
            if g.winner == self:
                self.win_count += 1
            else:
                self.loss_count += 1
    
    def win_percent(self):
        return float(self.win_count) / (self.win_count + self.loss_count)
    
    def __eq__(self, other):
        return self.id == other.id

#
# Information about a single game
#
class Game:
    def __init__(self, home, away, home_score, away_score, date, neutral):
        self.home = home
        self.away = away
        self.home_score = home_score
        self.away_score = away_score
        self.date = date
        self.neutral = neutral
        
        if self.home_score > self.away_score:
            self.winner = self.home
            self.loser = self.away
            self.wscore = self.home_score
            self.lscore = self.away_score
        else:
            self.winner = self.away
            self.loser = self.home
            self.wscore = self.away_score
            self.lscore = self.home_score
    
    def pretty(self, team):
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
        self.total_teams = float(len(self.teams))
        
    def Rank(self):
        # This has the side effect of giving all FBS teams a ranking.
        # After this, FCS schools will still have a ranking of 0.
        self.order = self.order_by_win_percent()
        self.update_rankings()
        
        self.determine_strength_of_schedule()
        self.normalize_strength_of_schedule()
        self.update_rankings()
                
        for a in range(1, 50):
            self.order_by_win_over()
            self.normalize_win_over()
            self.update_rankings()
    
    def update_rankings(self):
        preorder = dict()
        self.order = dict()
        
        for id, team in self.teams.iteritems():
            tp = round(team.rank.total_points() * self.precision_digits)
            
            if tp in preorder.keys():
                preorder[tp].append(team)
            else:
                preorder[tp] = [team]
        
        revPos = 1
        
        for points in sorted(preorder.keys(), reverse=True):
            pos_list = list()
            
            for team in preorder[points]:
                pos_list.append(team)

            self.order[revPos] = pos_list
            revPos += len(preorder[points])
        
        for rank, teams in self.order.iteritems():
            for team in teams:
                team.rank.ranking = rank
    
    def get_ranking_display(self, count=0):
        output = ''
        i = 0
        
        for rank in sorted(self.order.keys()):
            for team in self.order[rank]:
                if count != 0 and i >= count:
                    break
                
                i += 1
                
                output += str(rank).rjust(3) + '  ' + str(team).ljust(20) + ' Total points: ' + ('%.3f' % team.rank.total_points())
                output += '\t(' + str(team.win_count).rjust(2) + ' - ' + str(team.loss_count) + ')'
                output += '\t Win Over: ' + ('%.3f' % (team.rank.win_over * team.rank.win_over_weight)).rjust(7)
                output += '\t Win Per: ' + ('%.3f' % (team.rank.win_percent * team.rank.win_percent_weight)).rjust(6)
                output += '\t SoS: ' + ('%.3f' % (team.rank.strength_of_schedule * team.rank.strength_of_schedule_weight))
                output += ' (' + str(team.opp_win_count) + ' - ' + str(team.opp_loss_count) + ', ' + ('%.3f' % team.rank.strength_of_schedule) + ')'
                output += '\n'
        
        return output
    
    def order_by_win_percent(self):
        ordered = dict()
        return_order = dict()
        
        for id in sorted(self.teams.keys()):
            team = self.teams[id]
            winPer = team.win_percent()
            team.rank.win_percent = winPer
            
            if winPer in ordered.keys():
                ordered[winPer].append(team)
            else:
                ordered[winPer] = [team]
        
        revPos = 1
        pos = self.total_teams
        
        for winPer in sorted(ordered.keys(), reverse=True):
            pos_list = list()
            
            for team in ordered[winPer]:
                pos_list.append(team)

            pos -= len(ordered[winPer])
            return_order[revPos] = pos_list
            revPos += len(ordered[winPer])
        
        return return_order
    
    def order_by_win_over(self):
        for id, team in self.teams.iteritems():
            points = 0
            
            for dt, game in team.games.iteritems():
                if game.winner == team:
                    points += self.determine_game_points(game)
            
            team.rank.win_over = points
    
    def normalize_win_over(self):
        max = 0
        min = 101
        
        for id, team in self.teams.iteritems():
            if team.rank.win_over > max:
                max = team.rank.win_over
            
            if team.rank.win_over != 0 and team.rank.win_over < min:
                min = team.rank.win_over
        
        assert max > 0 and min > 0 and min < 101
        assert max - min > 0

        for id, team in self.teams.iteritems():
            team.rank.win_over = (team.rank.win_over - min) / (max - min)
    
    def determine_strength_of_schedule(self):        
        for id, team in self.teams.iteritems():
            opponent_wins = 0
            opponent_losses = 0
            
            for dt, game in team.games.iteritems():
                if game.winner == team:
                    opponent = game.loser
                else:
                    opponent  = game.winner
                
                # Only count FBS opponents.
                if opponent.is_fbs:
                    opponent_wins += opponent.win_count
                    opponent_losses += opponent.loss_count
            
            # Some transitional teams (FCS -> FBS) teams will have 0 FBS opponents. Their SoS will be 0.
            if opponent_wins + opponent_losses == 0:
                team.rank.strength_of_schedule = 0
            else:
                team.rank.strength_of_schedule = float(opponent_wins) / (opponent_wins + opponent_losses)
            
            team.opp_win_count = opponent_wins
            team.opp_loss_count = opponent_losses
    
    def normalize_strength_of_schedule(self):
        max = 0
        min = 101
        
        for id, team in self.teams.iteritems():
            if team.rank.strength_of_schedule > max:
                max = team.rank.strength_of_schedule
            
            if team.rank.strength_of_schedule != 0 and team.rank.strength_of_schedule < min:
                min = team.rank.strength_of_schedule
        
        assert max > 0 and min > 0 and min < 101
        assert max - min > 0

        for id, team in self.teams.iteritems():
            team.rank.strength_of_schedule = (team.rank.strength_of_schedule - min) / (max - min)
    
    def determine_game_points(self, game):
        bucket_size = 5
        num_buckets = math.ceil(self.total_teams / bucket_size)
        
        # Only count points for wins over an FBS school.
        if game.loser.is_fbs:
            gamepoints = num_buckets - math.floor(game.loser.rank.ranking / bucket_size)
        else:
            gamepoints = 0
            
        return gamepoints

#
# Parses a row of the CSV file, creates games and teams as needed
#
def add_game(row, fbs_teams, all_teams):
    neutral = False

    if row['Institution ID'] in all_teams:
        h = all_teams[row['Institution ID']]
        
        # Hey, this team showed up in the left column! They're an FBS team.
        if row['Institution ID'] not in fbs_teams:
            fbs_teams[h.id] = h
            h.is_fbs = True
    else:
        h = Team(row['Institution ID'], row['Institution'])
        fbs_teams[h.id] = h
        all_teams[h.id] = h
        h.is_fbs = True

    if row['Opponent ID'] in all_teams:
        a = all_teams[row['Opponent ID']]
    else:
        a = Team(row['Opponent ID'], row['Opponent Name'])
        all_teams[a.id] = a
        
    if row['Location'] == 'Neutral Site':
        neutral = True

    if row['Location'] == 'Away':
        temp = h
        h = a
        a = temp
        home_score = int(row['Score Against'])
        away_score = int(row['Score For'])
    else:
        home_score = int(row['Score For'])
        away_score = int(row['Score Against'])
    
    date_sub_parts = row['Game Date'].split('/') # Format: MM/DD/YY
    # BUG: Reverse Y2K bug? Yes. Fix.
    d = date(2000 + int(date_sub_parts[2]), int(date_sub_parts[0]), int(date_sub_parts[1]))
    
    g = Game(h, a, home_score, away_score, d, neutral)
    h.add_game(g)
    a.add_game(g)

#
# Prints all teams and their game results
#
def print_all_teams(fbs_teams):
    for id in sorted(fbs_teams.keys()):
        team = fbs_teams[id]
        print str(team.rank.ranking).rjust(3) + ' ' + str(team) + ' (' + str(team.win_count) + ' - ' + str(team.loss_count) + ') '
        
        for date in sorted(team.games.keys()):
            print team.games[date].pretty(team)
        
        print

#
# Main
#
fbs_team_list = dict()
all_team_list = dict()

reader = csv.DictReader(open('fbs.2011.final.csv', 'rb'), delimiter=',', quotechar='"')

for row in reader:
    add_game(row, fbs_team_list, all_team_list)

rank = Ranking(fbs_team_list)
rank.Rank()
print rank.get_ranking_display(25)

#print_all_teams(fbs_team_list)
