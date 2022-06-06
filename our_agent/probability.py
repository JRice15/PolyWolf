import math
from collections import defaultdict
import numpy as np

from role_estimation.load_rnn_estimator import RoleEstimatorRNN
import logger

class Estimator:
    def __init__(self, agent):
        self.agent = agent
        self.state = self.agent.state
        self.role_estimator = RoleEstimatorRNN()
        self.predictions = None
        self.current_pred = None
        self.past_preds = []
        self.correct_preds = 0
        self.total_preds = 0
    def update(self, base_info, diff_data, request):
        try:
            predictions = self.role_estimator.update_and_predict(base_info=base_info, diff_data=diff_data, request=request)
        except KeyError: # If there's a word in here we don't have a one-hot encoding for.
            predictions = None # Will only happen if an agent is saying something nonsensical, like claiming to be a role that does not exist in this game.
        if type(predictions) != type(None) and not predictions.empty:
            self.predictions = predictions.to_numpy()
            offset = max(abs(min(self.predictions.flatten())), abs(max(self.predictions.flatten())))
            for row in self.predictions:
                row += offset
                row /= sum(row)
        if request == 'DAILY_INITIALIZE':
            self.past_preds.append(self.current_pred)
        # Report accuracy statistics.
        if request == 'FINISH':
            logger.log('---FINISH---')
            #logger.log(f'My ID: {self.agent.id}')
            for player in self.state.player_list:
                #logger.log(f'{player}:{self.state.get_player_accuracy(player)}')
                logger.log(f'{player}:{self.state.voter_accuracy_good[player]}/{self.state.votes_total_good[player]}')
            self.correct_preds += self.state.get_prediction_accuracy(self.past_preds)
            self.total_preds += len(self.past_preds)
            self.past_preds = []
            self.predictions = None
            #logger.log(f'PREDICTOR ACCURACY: {self.correct_preds/self.total_preds}')
        if request == 'DAILY_INITIALIZE':
            if self.agent.role == 'BODYGUARD' and self.state.day > 1 and (not len(self.state.murdered_players.values()) or max(self.state.murdered_players.values()) != self.state.day):
                self.state.confirmed[self.agent.target] = 'HUMAN'
    def prior(self, player):
        evils = self.state.roles_counts['WEREWOLF'] + self.state.roles_counts['POSSESSED']
        total = len(self.state.player_list)
        for player in self.state.confirmed.keys():
            if self.state.confirmed[player] == 'WEREWOLF':
                evils -= 1
            total -= 1
        if player == self.agent.id:
            return 0
        if player in self.state.confirmed.keys():
            if self.state.confirmed[player] == 'WEREWOLF':
                return 1
            return self.state.roles_counts['POSSESSED'] / total
        return evils / total
    def estimate_suspicions(self):
        if type(self.predictions) == type(None):
            suspicions = {player_id:self.prior(player_id) for player_id in self.state.current_living_players}
        else:
            suspicions = self.predictions[:,-1] + self.predictions[:,2] # Prob Werewolf + Possessed
            suspicions = {player_id:suspicions[player_id-1] for player_id in self.state.current_living_players}
            for agentid in suspicions:
                if agentid in self.state.confirmed:
                    if self.state.confirmed[agentid] == 'WEREWOLF':
                        suspicions[agentid] = 1
                    else:
                        suspicions[agentid] = self.predictions[:,2][agentid-1]
        return suspicions
    def prob_given_player(self, player_accuracy_village, player_accuracy_werewolf, player_sus):
        if player_accuracy_werewolf == None: player_accuracy_werewolf = 0
        if player_accuracy_village == None: return None
        return (player_sus * player_accuracy_werewolf)  +  ((1-player_sus) * player_accuracy_village)
    # If you have a bunch of different measurements of the probability that X player is evil, how do you combine them?
    # Initial attempts treated all of these probabilities as totally independent measurements, and did some math combined with an a priori idea of how likely a player is to be evil to come up with a solution. But that didn't work out so well.
    # Because everybody's votes, and our own, are *not* independent. Those decisions are made based on a lot of the same information, and often with somewhat similar methods.
    # So instead of multiplying the probabilities, it actually just works better to take the most confident measurement, and take that one as truth.
    # Todo: If there is time, it would be nice to do a comprehensive test to see if max() or average() yields better results. My guess is max() is better but idk.
    def aggregate_probs(self, probs, prior):
        probs = [prob for prob in probs if prob != None]
        all = probs + [prior]
        return max(all)
        #if 1 in probs or prior == 1: return 1
        #if 0 in probs or prior == 0: return 0
        #if len(probs) == 0: return prior
        #ratio_true = math.exp( (sum([math.log(prob)-math.log(prior) for prob in probs])+math.log(prior)) - (sum([math.log(1-prob)-math.log(1-prior) for prob in probs])+math.log(1-prior)) )
        #prob_true = ratio_true / (ratio_true+1)
        #return prob_true
    def vote_analysis(self):
        evil_probabilities = self.estimate_suspicions()
        '''
        probs_table = {agentid:[evil_probabilities[agentid]] for agentid in self.state.current_living_players} #defaultdict(list)
        for agentid in self.state.votes_current.keys():
            if agentid == self.agent.id: continue
            prob = self.prob_given_player(self.state.get_player_accuracy(agentid, werewolf=False), self.state.get_player_accuracy(agentid, werewolf=True), evil_probabilities[agentid])
            target = self.state.votes_current[agentid]
            if target not in self.state.current_living_players: continue
            probs_table[target].append(prob)
        if self.state.games > 30: prob = (self.correct_preds / self.total_preds)
        else: prob = 1
        self.current_pred = max(evil_probabilities, key=evil_probabilities.get)
        probs_table[self.current_pred].append(prob)
        for target in probs_table.keys():
            evil_probabilities[target] = self.aggregate_probs(probs_table[target], self.prior(target))
        '''
        return evil_probabilities