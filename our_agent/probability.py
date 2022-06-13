import math
from collections import defaultdict
import numpy as np

from role_estimation.load_rnn_estimator import RoleEstimatorRNN
import logger

prob_map = {'BODYGUARD':0, 'MEDIUM':1, 'POSSESSED':2, 'SEER':3, 'VILLAGER':4, 'WEREWOLF':5}

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
        self.last_recorded = 0
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
        if request == 'DAILY_INITIALIZE' and self.state.day > 1 and self.state.day != self.last_recorded:
            self.last_recorded = self.state.day
            self.past_preds.append(self.current_pred)
        # Report accuracy statistics.
        if request == 'FINISH':
            if self.total_preds > 0:
                logger.log(f'PREDICTOR ACCURACY: {self.correct_preds/self.total_preds}')
            logger.log('---FINISH---')
            #logger.log(f'My ID: {self.agent.id}')
            for player in self.state.player_list:
                #logger.log(f'{player}:{self.state.get_player_accuracy(player)}')
                logger.log(f'{player}:{self.state.voter_accuracy_good[player]}/{self.state.votes_total_good[player]}')
            self.correct_preds += self.state.get_prediction_accuracy(self.past_preds)
            self.total_preds += len(self.past_preds)
            self.past_preds = []
            self.predictions = None
            self.last_recorded = 0
        if request == 'DAILY_INITIALIZE':
            if self.agent.role == 'BODYGUARD' and self.state.day > 1 and (not len(self.state.murdered_players.values()) or max(self.state.murdered_players.values()) != self.state.day):
                self.state.confirmed[self.agent.target] = 'HUMAN'
    def prior(self, player):
        evils = self.state.roles_counts['WEREWOLF'] + self.state.roles_counts['POSSESSED']
        total = len(self.state.player_list)
        for pid in self.state.confirmed.keys():
            if self.state.confirmed[pid] == 'WEREWOLF':
                evils -= 1
            total -= 1
        if player == self.agent.id:
            return 0
        if player in self.state.confirmed.keys():
            if self.state.confirmed[player] == 'WEREWOLF':
                return 1
            return self.state.roles_counts['POSSESSED'] / total
        return evils / total
    '''
    def prior_possessed(self, player):
        if player == self.agent.id: return 0
        total = len(self.state.player_list)
        for pid in self.state.confirmed.keys():
            if self.state.confirmed[pid] == 'WEREWOLF':
                if player == pid: return 0
                total -= 1
        return self.state.roles_counts['POSSESSED'] / total
    '''
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
    '''
    def estimate_possessed(self):
        if type(self.predictions) == type(None):
            suspicions = {player_id:self.prior(player_id) for player_id in self.state.current_living_players}
        else:
            suspicions = self.predictions[:,2]
            suspicions = {player_id:suspicions[player_id-1] for player_id in self.state.current_living_players}
        return suspicions
    '''
    def prob_given_player(self, player_accuracy_village, player_accuracy_werewolf, player_sus):
        if player_accuracy_werewolf == None: player_accuracy_werewolf = 0
        if player_accuracy_village == None: return None
        return (player_sus * player_accuracy_werewolf)  +  ((1-player_sus) * player_accuracy_village)
    # If you have a bunch of different measurements of the probability that X player is evil, how do you combine them?
    # Initial attempts treated all of these probabilities as totally independent measurements, and did some math combined with an a priori idea of how likely a player is to be evil to come up with a solution. But that didn't work out so well.
    # Because everybody's votes, and our own, are *not* independent. Those decisions are made based on a lot of the same information, and often with somewhat similar methods.
    # So instead of multiplying the probabilities, it actually just works better to take the most confident measurement, and take that one as truth.
    # Todo: If there is time, it would be nice to do a comprehensive test to see if max() or average() yields better results. My guess is max() is better but idk.
    def aggregate_probs_dependent(self, probs):
        probs = [prob for prob in probs if prob != None]
        return max(probs)
    def aggregate_probs_independent(self, probs, prior):
        probs = [prob for prob in probs if prob != None]
        if 1 in probs or prior == 1: return 1
        if 0 in probs or prior == 0: return 0
        if len(probs) == 0: return prior
        ratio_true = math.exp( (sum([math.log(prob)-math.log(prior) for prob in probs])+math.log(prior)) - (sum([math.log(1-prob)-math.log(1-prior) for prob in probs])+math.log(1-prior)) )
        prob_true = ratio_true / (ratio_true+1)
        return prob_true
    def vote_analysis_neural(self):
        evil_probabilities = self.estimate_suspicions()
        return evil_probabilities
    def vote_analysis_aggregate(self):
        evil_probabilities = self.estimate_suspicions()
        self.current_pred = max(evil_probabilities, key=evil_probabilities.get)
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
            evil_probabilities[target] = self.aggregate_probs_dependent(probs_table[target])#, self.prior(target))
        return evil_probabilities
    def loss_analysis(self, alignment='GOOD'):
        evil_probabilities = self.estimate_suspicions()
        loss_table = defaultdict(float)
        for agentid in self.state.current_living_players:
            if agentid == self.agent.id: continue
            if self.state.games_good[agentid] == 0: continue
            if self.state.games_evil[agentid] == 0: continue
            good_winrate = self.state.wins_good[agentid] / self.state.games_good[agentid]
            evil_winrate = self.state.wins_evil[agentid] / self.state.games_evil[agentid]
            if alignment == 'GOOD':
                loss_table[agentid] = self.prob_given_player((1-good_winrate), evil_winrate, evil_probabilities[agentid])
            else:
                loss_table[agentid] = self.prob_given_player(good_winrate, (1-evil_winrate), evil_probabilities[agentid])
        return loss_table
    def prob_role_is_dead(self, role):
        if type(self.predictions) == type(None):
            return (self.state.roles_counts[role] > 0)
        else:
            probs = self.predictions[:,prob_map[role]]
            probs = [1-prob for prob in probs]
            return np.prod(probs)

    #def estimate_role_alive(self):
    # Add up the neural estimate for all of a certain role, living vs. dead, as a probability
    #player_will_win(self, player_winrate_good, player_winrate_evil, player_sus)