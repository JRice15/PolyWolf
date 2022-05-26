# Agent that always claims its role and the action it took.
# Otherwise takes random actions and votes randomly.

import random

import aiwolfpy
import aiwolfpy.contentbuilder as cb

from base_agent import Agent

class FrankAgent(Agent):
    def __init__(self, agent_name):
        super().__init__(agent_name)
        self.claimed = False
        self.shared = False
        self.target = -1
    def guard(self):
        valid_targets = self.state.current_living_players.copy()
        valid_targets.remove(self.id)
        self.target = random.choice(valid_targets)
        return self.target
    def divine(self): # A smarter agent would presumably at least avoid scanning someone who is about to get voted off, but this is not that agent.
        valid_targets = self.state.current_living_players.copy()
        valid_targets.remove(self.id)
        for previously_scanned in self.state.seer_results.keys():
            if previously_scanned in valid_targets:
                valid_targets.remove(previously_scanned)
        self.target = random.choice(valid_targets)
        return self.target
    def talk(self):
        if not self.claimed:
            self.claimed = True
            return cb.comingout(self.id, self.role)
        if not self.shared:
            self.shared = True
            if self.role == 'MEDIUM':
                for dead in self.state.recently_dead_players:
                    if dead in self.state.medium_results.keys():
                        return cb.identified(dead,self.state.medium_results[dead])
            elif self.role == 'BODYGUARD':
                return cb.guarded(self.target)
            elif self.role == 'SEER':
                if self.target in self.state.seer_results.keys():
                    return cb.divined(self.target, self.state.seer_results[self.target])
            elif self.role == 'WEREWOLF':
                return cb.guarded(self.state.last_attacked_player).replace('GUARDED','ATTACKED')
        return cb.over()
    def update(self, base_info, diff_data, request):
        super().update(base_info, diff_data, request)
        if request == 'DAILY_INITIALIZE':
            self.claimed = False
            self.shared = False

agent = FrankAgent('frank')

if __name__ == '__main__':
    aiwolfpy.connect_parse(agent)
