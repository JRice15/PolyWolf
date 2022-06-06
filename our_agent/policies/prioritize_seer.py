from policies.base_agenda import Agenda
from aiwolfpy import contentbuilder as cb

import random

# Agent prioritizes the lives of those who it thinks might be the seer. Both to end them as a werewolf, or to protect them as a bodyguard.
class SeerPriority(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['attack'] = 1
        self.weights['protect'] = 1
        self.weights['talk'] = 2
        self.weights['vote'] = 0.5
        self.last_claimed = None
        self.last_shared = None
    def reset(self):
        self.last_claimed = None
        self.last_shared = None
    def reset(self):
        claimed = False
    # The seer must die!
    def attack(self):
        if type(self.agent.estimator.predictions) == type(None): return None
        seer_probabilities = self.agent.estimator.predictions[:,3] # Column 3 = Seer predictions
        seer_probabilities = {player_id:seer_probabilities[player_id-1] for player_id in self.agent.state.current_living_players}
        return seer_probabilities
    # The seer must survive!
    def protect(self):
        return self.attack()
    # If you are the seer, come forward when you have a guilty result.
    def talk(self):
        if self.agent.role == 'SEER':
            '''
            for claimant in self.agent.state.claims:
                if self.agent.state.claims[claimant] == 'SEER' and claimant != self.agent.id:
                    if self.last_claimed != self.agent.state.day:
                        self.last_claimed = self.agent.state.day
                        return {cb.comingout(self.agent.id, 'SEER'):1}
            '''
            if self.agent.target in self.agent.state.confirmed.keys() and self.agent.state.confirmed[self.agent.target] == 'WEREWOLF':
                if self.last_claimed != self.agent.state.day:
                    self.last_claimed = self.agent.state.day
                    return {cb.comingout(self.agent.id, 'SEER'):1}
            if self.last_claimed:
                if self.last_shared != self.agent.state.day:
                    self.last_shared = self.agent.state.day
                    if self.agent.target in self.agent.state.confirmed:
                        return {cb.divined(self.agent.target, self.agent.state.confirmed[self.agent.target]):1}
                    else: # Only happens if our scan target died last night, in which case they are still confirmed human.
                        return {cb.divined(self.agent.target, 'HUMAN'):1}
                if self.agent.id in self.agent.state.claims_results:
                    for sus in self.agent.state.claims_results[self.agent.id]['WEREWOLF']:
                        if sus in self.agent.state.current_living_players:
                            if random.randint(1,5) == 5:
                                return {cb.divined(sus, 'WEREWOLF'):0.25}
        return None
    # If you are a villager, follow the seer claims, unless you know the seer is bad, in that case vote for the fake seer.
    def vote(self):
        if self.agent.role == 'WEREWOLF' or self.agent.role == 'POSSESSED': return None
        if self.agent.role == 'SEER' and self.agent.target in self.agent.state.confirmed.keys() and self.agent.state.confirmed[self.agent.target] == 'WEREWOLF':
            return {self.agent.target:1}
        for claimant in self.agent.state.claims:
            if self.agent.state.claims[claimant] == 'SEER':
                if self.agent.role == 'SEER' or self.agent.id in self.agent.state.claims_results[claimant]['WEREWOLF']:
                    return {claimant:1}
                for player in self.agent.state.claims_results[claimant]['WEREWOLF']:
                    if player in self.agent.state.confirmed and self.agent.state.confirmed[player] == 'HUMAN':
                        return {claimant:1}
                for player in self.agent.state.claims_results[claimant]['HUMAN']:
                    if player in self.agent.state.confirmed and self.agent.state.confirmed[player] == 'WEREWOLF':
                        return {claimant:1}
        for claimant in self.agent.state.claims:
            if self.agent.state.claims[claimant] == 'SEER':
                return {werewolf:1 for werewolf in self.agent.state.claims_results[claimant]['WEREWOLF'] if werewolf in self.agent.state.current_living_players}
        return None
