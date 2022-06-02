# An initial stab at a policy-based werewolf agent.
# Specify some list of paremters in a policy-space and it will play according to those settings.
# The goal is that a wide variety of possible rule-based approaches can be contained in the policy-space, and the best one can be searched for algorithmically.

import math
from collections import defaultdict

import aiwolfpy
import aiwolfpy.contentbuilder as cb

from base_agent import Agent
from state import log

# Three classes:
# Agent Class : Ties everything together and plays the game
# Predictor Class : Neural net, bayesian statistics, constraints estimation
# Agenda Class : Various agendas with differing weights depending on role and action currently being pursued

POLICY = {
    'fakeclaim':0,
    'vote_sus':1,
    'vote_diversify':1,
    'vote_fear':0.3,
    'vote_grudge_short':0.5,
    'vote_grudge_long':0.5,

    'ww_claim':0.2,
    'ww_fakeclaim':0.1,
    'ww_vote_bus':0.1,
    'ww_vote_fear':1,
    'ww_vote_grudge_short':1,
    'ww_vote_grudge_long':1,
    'ww_kill_fear':1,
    'ww_kill_grudge_short':1,
    'ww_kill_grudge_long':1,

    'possessed_claim':0.5,
    'possessed_fakeclaim':0.5,
    'possessed_vote_fear':1,
    'possessed_vote_grudge_short':1,
    'possessed_vote_grudge_long':1,

    'seer_claim':1,
    'seer_scan_sus':1,
    'seer_scan_fear':1,
    'seer_scan_grudge':1,
    'seer_scan_surv':1,
    'seer_share_inno':1,
    'seer_share_guilty':1,

    'medium_claim':1,
    'medium_share_inno':1,
    'medium_share_guilty':1,

    'bg_claim':1,
    'bg_protect_trusts':1,
    'bg_protect_winners':1,
    'bg_protect_allies':1,
    'bg_protect_claimants':1,
    'bg_share_protect_failed':1,
    'bg_share_protect_successful':1,
}

'''
# TODO: Incorporate neural-net predictor into an agent.
# TODO: Make system that records votewise accuracy over each role, as well as good / evil in general.
# TODO: People who are attacked or medium-flip human aren't confirmed good, they could still be possessed.
# TODO: Calculate plausibility given player is evil, based on:
#   -The estimated probability other people who suspect them are correct,
#   -The probability that the player is displaying the accuracy rate observed in this game, given that they are evil vs. given that they are good.
#   -The summed probability of choosing N other wolves from the player list, assuming this person is a wolf. Are there enough potential teammates?
'''

# A modular behavior agenda that can be linearly combined with other behavior agendas based on policy weights.
# For each action, the convention is to return a (possibly incomplete) ditionary of action:confidence pairs, or "None" if this agenda has no opinion about that particular action.
class Agenda:
    def __init__(self):
        self.name = 'Error'
    def talk(self, state):
        return None
    def vote(self, state):
        return None
    def attack(self, state):
        return None
    def protect(self, state):
        return None
    def scan(self, state):
        return None

# Vote for the person that we estimate is most likely to be a werewolf.
class Analysis(Agenda):
    pass

# Push for votes on people who don't currently have any votes.
class Dissent(Agenda):
    def __init__(self):
        self.name = 'dissent'
    def vote(self, state):
        tally = state.vote_tally()
        return {id:0 if tally[id] > 0 else id:1 for id in state.currently_living_players}

# Push to take action against players that have a high win rate in past games on the opposite team as yours.
class Fear(Agenda):
    def __init__(self):
        self.name = 'fear'
    def vote(self, state):
        tally = state.vote_tally()
        return {id:0 if tally[id] > 0 else id:1 for id in state.currently_living_players}

# Push to take action on behalf of players that have a high win rate in past games on the same team as yours.
class Elitism(Agenda):
    def __init__(self):
        self.name = 'elitism'
    def vote(self, state):
        tally = state.vote_tally()
        return {id:0 if tally[id] > 0 else id:1 for id in state.currently_living_players}

class PolicyAgent(Agent):
    def __init__(self, agent_name, policy):
        super().__init__(agent_name)
        self.policy = policy
        self.agendas = []
        self.estimator = None
        self.confirmed = {}
        self.reads = {}
        self.my_vote = -1
        self.my_target = -1

    def weighted_average(self, seq, weights):
        return sum([s*w for s,w in zip(seq,weights)]) / sum(weights)

    def choose_vote(self):
        self.reads = self.vote_analysis()
        voting_values = {agenda.name:agenda.vote() for agenda in self.agendas}
        aggregate_value = {id:self.weighted_average([voting_values[agenda][id] for agenda in voting_values.keys() if id in voting_values[agenda].keys()],[self.policy[agenda] for agenda in voting_values.keys() if id in voting_values[agenda].keys()]) for id in self.state.current_living_players}
        vote = max(aggregate_value, key=aggregate_value.get)
        return vote

    def update(self, base_info, diff_data, request):
        super().update(base_info, diff_data, request)
        if request == 'FINISH':
            log('---FINISH---')
            log(f'My ID: {self.id}')
            self.confirmed = {self.id:'HUMAN'}
            for predictor in self.predictors:
                predictor.correct += self.state.get_prediction_accuracy(predictor.predictions)
                predictor.total += len(predictor.predictions)
                predictor.predictions = []
                log(f'PREDICTOR ACCURACY: {predictor.accuracy()}')
            for player in self.state.player_list:
                log(f'AGENT {player} ACCURACY: {self.state.get_player_accuracy(player)}')
        elif request == 'DAILY_INITIALIZE':
            if self.role == 'BODYGUARD' and self.state.day > 1 and len(self.state.night_killed_players) == 0:
                self.confirmed[self.my_target] = 'HUMAN'
            elif self.role == 'MEDIUM':
                for player in self.state.recently_dead_players:
                    if player in self.state.medium_results.keys():
                        self.confirmed[player] = self.state.medium_results[player]
            elif self.role == 'SEER':
                if self.my_target in self.state.seer_results.keys():
                    self.confirmed[self.my_target] = self.state.seer_results[self.my_target]
            for player in self.state.recently_dead_players:
                if player in self.state.night_killed_players:
                    self.confirmed[player] = 'HUMAN'

    def talk(self):
        try:
            target = self.choose_vote()
            if target and self.my_vote != target:
                self.my_vote = target
                return cb.vote(target)
        except: pass
        return cb.over()

    def whisper(self):
        return cb.over()

    def vote(self):
        return self.choose_vote()

    def attack(self):
        return self.id

    def divine(self):
        return self.id

    def guard(self):
        return self.id

agent = PolicyAgent('policy', POLICY)

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
