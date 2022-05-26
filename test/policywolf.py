# An initial stab at a policy-based werewolf agent.
# Specify some list of paremters in a policy-space and it will play according to those settings.
# The goal is that a wide variety of possible rule-based approaches can be contained in the policy-space, and the best one can be searched for algorithmically.

from email.mime import base
import math
from collections import defaultdict

import aiwolfpy
import aiwolfpy.contentbuilder as cb

from base_agent import Agent
from state import log

POLICY = {
    'prior_cutoff':4,
    'prior_contrarian':1,

    'v_fakeclaim':0,
    'v_vote_neural':1,
    'v_vote_prob':1,
    'v_vote_constraints':1,
    'v_vote_diversify':1,
    'v_vote_fear':0.3,
    'v_vote_grudge_short':0.5,
    'v_vote_grudge_long':0.5,

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
    'medium_share_v':1,
    'medium_share_ww':1,
    'medium_share_possessed':1,
    'medium_share_seer':1,
    'medium_share_bg':1,

    'bg_claim':1,
    'bg_share_protect':1,
    'bg_protect_trusts':1,
    'bg_protect_winners':1,
    'bg_protect_allies':1,
    'bg_protect_claimants':1,
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

class Predictor:
    def __init__(self, prior):
        self.predictions = []
        self.correct = 0
        self.total = 0
        self.prior = prior
    def accuracy(self):
        if self.total == 0: return 1.
        else: return self.correct / self.total
    def predict(self, state):
        self.predictions.append(0)

class ContrarianPredictor(Predictor):
    def predict(self, state):
        try: self.predictions.append(state.vote_tally().most_common()[-1][0])
        except: self.predictions.append(state.current_living_players[0])

class PolicyAgent(Agent):
    def __init__(self, agent_name, policy):
        super().__init__(agent_name)
        self.policy = policy
        self.predictors = [ContrarianPredictor(self.policy['prior_contrarian'])]
        self.my_vote = -1
        self.my_target = -1
        self.spoke = False
    
    def initialize(self, base_info, diff_data, game_setting):
        super().initialize(base_info, diff_data, game_setting)
        self.confirmed = {self.id:'HUMAN'}

    def weighted_average(self, seq, weights):
        return sum([s*w for s,w in zip(seq,weights)]) / sum(weights)

    # Just from the number of players alive and any information that we can mechanically confirm with our own role, what is the worst-case proportion of evil players in the game?
    def prior(self):
        return 4/14
        #evils = self.state.roles_counts['WEREWOLF'] + self.state.roles_counts['POSSESSED']
        #total = len(self.state.player_list)
        #for player in self.confirmed.keys():
        #    if self.confirmed[player] == 'WEREWOLF':
        #        evils -= 1
        #    total -= 1
        #return evils/total

    # Right now just returns an even distribution on everyone, and the definite result on those who are hard-confirmed. Could very easily be improved with a role estimator neural network.
    def estimate_suspicion(self, player):
        #if player in self.confirmed.keys():
        #    if self.confirmed[player] == 'WEREWOLF':
        #        return 1
        #    return 0
        return self.prior()

    # The probability that a given player is either not evil and not mistaken about their vote, or evil and throwing a teammate under the bus.
    # In other words, the probability that a player's vote is in fact correct.
    def prob_given_player(self, player_accuracy_village, player_accuracy_werewolf, player_sus):
        if player_accuracy_werewolf == None: player_accuracy_werewolf = 0
        if player_accuracy_village == None: return None
        return (player_sus * player_accuracy_werewolf)  +  ((1-player_sus) * player_accuracy_village)

    # Given that a bunch of players or predictors voted to execute some person, what is the actual probability that they are either 1) all correct or 2) all mistaken.
    def aggregate_probs(self, probs, prior):
        if 1 in probs or prior == 1: return 1
        if 0 in probs or prior == 0: return 0
        probs = [prob for prob in probs if prob != None]
        if len(probs) == 0: return prior
        ratio_true = math.exp( (sum([math.log(prob)-math.log(prior) for prob in probs])+math.log(prior)) - (sum([math.log(1-prob)-math.log(1-prior) for prob in probs])+math.log(1-prior)) )
        prob_true = ratio_true / (ratio_true+1)
        return prob_true
    
    # Based on our own predictions and other people's votes, taking into account the track record of each information source and that other people might be lying, what is the probability that each player is evil?
    def votes_current_analysis(self):
        prior = self.prior()
        probs_table = defaultdict(list)
        evil_probabilities = {target:prior for target in self.state.player_list}
        for agentid in self.state.votes_current.keys():
            if agentid == self.id: continue
            prob = self.prob_given_player(self.state.get_player_accuracy(agentid, werewolf=False), self.state.get_player_accuracy(agentid, werewolf=True), self.estimate_suspicion(agentid))
            target = self.state.votes_current[agentid]
            probs_table[target].append(prob)
            log(f'Agent {agentid} sussed {target} with odds of correctness of {prob}')
        #for agentid in self.state.player_list:
        #    if agentid not in self.state.current_living_players and len(self.state.votes_history[agentid]):
        #        prob = self.prob_given_player(self.state.get_player_accuracy(agentid, werewolf=False), self.state.get_player_accuracy(agentid, werewolf=True), self.estimate_suspicion(agentid))
        #        target = self.state.votes_history[agentid][-1]
        #        probs_table[target].append(prob)
        #        log(f'Deceased Agent {agentid} last sussed {target} with odds of correctness of {prob}')
        for predictor in self.predictors:
            if self.state.games > self.policy['prior_cutoff']: prob = predictor.accuracy()
            else: prob = predictor.prior
            target = predictor.predictions[-1]
            probs_table[target].append(prob)
            log(f'Predictor sussed {target} with odds of correctness of {prob}')
        for target in probs_table.keys():
            evil_probabilities[target] = self.aggregate_probs(probs_table[target], prior)
        for player in self.confirmed.keys():
            if self.confirmed[player] == 'WEREWOLF': evil_probabilities[player] = 1
            else: evil_probabilities[player] = 0
        return evil_probabilities

    # Analyze the votes of past cycles in a similar fashion.
    # def votes_history_analysis(self):
    #     prior = self.prior()
    #     probs_table = defaultdict(list)
    #     evil_probabilities = {target:prior for target in self.state.player_list}
    #     for agentid in self.state.votes_history.keys():
    #         if agentid == self.id: continue
    #         prob = self.prob_given_player(self.state.get_player_accuracy(agentid, werewolf=False), self.state.get_player_accuracy(agentid, werewolf=True), self.estimate_suspicion(agentid))
    #         for vote in self.state.votes_history[agentid]:
    #             probs_table[vote].append(prob)
    #             log(f'Agent {agentid} previously sussed {vote} with odds of correctness of {prob}')
    #     for target in probs_table.keys():
    #         evil_probabilities[target] = self.aggregate_probs(probs_table[target], prior)
    #     for player in self.confirmed.keys():
    #         if self.confirmed[player] == 'WEREWOLF': evil_probabilities[player] = 1
    #         else: evil_probabilities[player] = 0
    #     return evil_probabilities

    def choose_vote(self):
        for predictor in self.predictors:
            predictor.predict(self.state)
        # if self.policy['v_vote_prob_current']: evil_probabilities_i = self.votes_current_analysis()
        # else: evil_probabilities_i = {id:0 for id in self.state.player_list}
        # if self.policy['v_vote_prob_history']: evil_probabilities_ii = self.votes_history_analysis()
        # else: evil_probabilities_ii = {id:0 for id in self.state.player_list}
        # evil_probabilities = {id:self.weighted_average([evil_probabilities_i[id],evil_probabilities_ii[id]],[self.policy['v_vote_prob_current'],self.policy['v_vote_prob_history']]) for id in self.state.player_list}
        # log(f'Evil Probabilities (Averaged): {evil_probabilities}')
        evil_probabilities = self.votes_current_analysis()
        vote = max(evil_probabilities, key=evil_probabilities.get)
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
            if self.role == 'BODYGUARD' and self.state.day != 1 and len(self.state.recently_dead_players) == 1:
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
