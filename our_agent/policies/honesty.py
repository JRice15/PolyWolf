from policies.base_agenda import Agenda
from aiwolfpy import contentbuilder as cb

import random

# Agent claims truthfully and shares any useful results, when they have information that is directly relevant.
class Honesty(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['talk'] = 2
        self.weights['vote'] = 0.5
        self.last_claimed = None
        self.last_shared = None
    def reset(self):
        self.last_claimed = None
        self.last_shared = None
    # If you are the seer, come forward when you have a guilty result.
    # If you are the medium, come forward if you can falsify the claims of a fake seer.
    # If you are the bodyguard, stay quiet: you can't self-protect.
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
                if self.last_claimed != self.agent.state.day:
                    self.last_claimed = self.agent.state.day
                    return {cb.comingout(self.agent.id, 'SEER'):1}
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
                                return {cb.divined(sus, 'WEREWOLF'):1}
        if self.agent.role == 'MEDIUM':
            for claimant in self.agent.state.claims:
                if self.agent.state.claims[claimant] == 'SEER' and claimant in self.agent.state.current_living_players:
                    for player in self.agent.state.claims_results[claimant]['WEREWOLF']:
                        if player in self.agent.state.confirmed and self.agent.state.confirmed[player] == 'HUMAN':
                            if self.last_claimed != self.agent.state.day:
                                self.last_claimed = self.agent.state.day
                                return {cb.comingout(self.agent.id, 'MEDIUM'):1}
                    for player in self.agent.state.claims_results[claimant]['HUMAN']:
                        if player in self.agent.state.confirmed and self.agent.state.confirmed[player] == 'WEREWOLF':
                            if self.last_claimed != self.agent.state.day:
                                self.last_claimed = self.agent.state.day
                                return {cb.comingout(self.agent.id, 'MEDIUM'):1}
            for dead in self.agent.state.executed_players:
                if self.agent.state.executed_players[dead] == self.agent.state.day:
                    if dead in self.agent.state.confirmed.keys():
                        if self.agent.state.confirmed[dead] == 'WEREWOLF':
                            if self.last_claimed != self.agent.state.day:
                                self.last_claimed = self.agent.state.day
                                return {cb.comingout(self.agent.id, 'MEDIUM'):1}
            if self.last_claimed:
                if self.last_shared != self.agent.state.day:
                    self.last_shared = self.agent.state.day
                    for dead in self.agent.state.executed_players:
                        if self.agent.state.executed_players[dead] == self.agent.state.day:
                            if dead in self.agent.state.confirmed.keys():
                                return {cb.identified(dead,self.agent.state.confirmed[dead]):1}
                for claimant in self.agent.state.claims:
                    if self.agent.state.claims[claimant] == 'SEER' and claimant in self.agent.state.current_living_players:
                        for player in self.agent.state.claims_results[claimant]['WEREWOLF']:
                            if player in self.agent.state.confirmed and self.agent.state.confirmed[player] == 'HUMAN':
                                if random.randint(1,5) == 5:
                                    return {cb.identified(player,'HUMAN'):1}
                        for player in self.agent.state.claims_results[claimant]['HUMAN']:
                            if player in self.agent.state.confirmed and self.agent.state.confirmed[player] == 'WEREWOLF':
                                if random.randint(1,5) == 5:
                                    return {cb.identified(player,'WEREWOLF'):1}
        if self.agent.role == 'BODYGUARD':
            return None
            '''
            if self.agent.target in self.agent.state.confirmed.keys():
                if self.last_claimed != self.agent.state.day:
                    self.last_claimed = self.agent.state.day
                    return {cb.comingout(self.agent.id, 'BODYGUARD'):1}
                if self.last_shared != self.agent.state.day:
                    self.last_shared = self.agent.state.day
                    return {cb.guarded(self.agent.target):1}
            '''
        return None
    # If a seer claimed and you know for sure they're lying, vote for 'em.
    def vote(self):
        if self.agent.role == 'WEREWOLF' or self.agent.role == 'POSSESSED': return None
        if self.agent.role == 'SEER' and self.agent.target in self.agent.state.confirmed.keys() and self.agent.state.confirmed[self.agent.target] == 'WEREWOLF':
            return {self.agent.target:1}
        for claimant in self.agent.state.claims:
            if self.agent.state.claims[claimant] == 'SEER' and claimant in self.agent.state.current_living_players:
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
