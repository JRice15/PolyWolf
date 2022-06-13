from policies.base_agenda import Agenda
from aiwolfpy import contentbuilder as cb
import random

# Agent tries to sabotage the village with fake role claims, depending on the context.
class Duplicity(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['talk'] = 0
        self.weights['vote'] = 0
        self.fakeclaimed = False
        self.fakeclaim_enabled = False
        self.fakeclaim_day = 0
        self.fake_guilty = None
        self.last_claimed = None
        self.last_shared = None
    def reset(self):
        self.fakeclaimed = False
        self.fakeclaim_enabled = (random.randint(1,15) < 9)
        self.fakeclaim_day = random.randint(1,8)
        self.fake_guilty = None
        self.last_claimed = None
        self.last_shared = None
    # Come out with fake claims, if the situation is right.
    def talk(self):
        if self.agent.role != 'WEREWOLF' and self.agent.role != 'POSSESSED': return None
        if self.fakeclaim_enabled and not self.fakeclaimed:
            for claimant in self.agent.state.claims:
                if claimant in self.agent.state.confirmed and self.agent.state.confirmed[claimant] == 'WEREWOLF':
                    self.fakeclaim_enabled = (random.randint(1,15) < 7) # Usually don't fakeclaim if one of our teammates already has
        if self.fakeclaim_enabled and not self.fakeclaimed:
            if self.agent.state.day >= self.fakeclaim_day:
                seer = False
                med = False
                bg = False
                for claimant in self.agent.state.claims:
                    if self.agent.state.claims[claimant] == 'SEER': seer=True
                    if self.agent.state.claims[claimant] == 'MEDIUM': med=True
                    if self.agent.state.claims[claimant] == 'BODYGUARD': bg=True
                if not seer:
                    self.fakeclaimed = 'SEER'
                    self.last_claimed = self.agent.state.day
                    return {cb.comingout(self.agent.id, 'SEER'):1}
                elif not med:
                    self.fakeclaimed = 'MEDIUM'
                    self.last_claimed = self.agent.state.day
                    return {cb.comingout(self.agent.id, 'MEDIUM'):1}
                elif not bg:
                    pass
                    #if self.agent.state.day > 1 and (not len(self.agent.state.murdered_players.values()) or max(self.agent.state.murdered_players.values()) != self.agent.state.day):
                    #    self.fakeclaimed = 'BODYGUARD'
                    #    self.last_claimed = self.agent.state.day
                    #    return {cb.comingout(self.agent.id, 'BODYGUARD'):1}
        if self.fakeclaimed:
            if self.last_claimed != self.agent.state.day:
                self.last_claimed = self.agent.state.day
                return {cb.comingout(self.agent.id, self.fakeclaimed):1}
            if self.last_shared != self.agent.state.day:
                self.last_shared = self.agent.state.day
                if self.fakeclaimed == 'SEER':
                    framed = self.agent.choose_vote()
                    while framed == self.agent.id:
                        framed = random.choice(self.agent.state.current_living_players)
                    self.fake_guilty = framed
                    return {cb.divined(self.fake_guilty, 'WEREWOLF'):1}
                if self.fakeclaimed == 'MEDIUM':
                    for dead in self.agent.state.executed_players:
                        if self.agent.state.executed_players[dead] == self.agent.state.day:
                            for claimant in self.agent.state.claims:
                                if self.agent.state.claims[claimant] == 'SEER' and claimant in self.agent.state.claims_results:
                                    # Corroborate our fellow werewolves.
                                    if claimant in self.agent.state.confirmed and self.agent.state.confirmed[claimant] == 'WEREWOLF':
                                        if dead in self.agent.state.claims_results[claimant]['WEREWOLF']:
                                            return {cb.identified(dead,'WEREWOLF'):1}
                                        elif dead in self.agent.state.claims_results[claimant]['HUMAN']:
                                            return {cb.identified(dead,'HUMAN'):1}
                                    # Contradict village seers, usually.
                                    else:
                                        self.fake_guilty = claimant
                                        if dead in self.agent.state.claims_results[claimant]['WEREWOLF']:
                                            return {cb.identified(dead,'HUMAN'):1}
                                        elif dead in self.agent.state.claims_results[claimant]['HUMAN']:
                                            return {cb.identified(dead,'WEREWOLF'):1}
                            if dead in self.agent.state.confirmed and self.agent.state.confirmed[dead] == 'WEREWOLF':
                                return {cb.identified(dead,'HUMAN'):1}
                            return {cb.identified(dead,random.choice(['HUMAN','WEREWOLF'])):1}
                if self.fakeclaimed == 'BODYGUARD':
                    if self.agent.state.day > 1 and (not len(self.agent.state.murdered_players.values()) or max(self.agent.state.murdered_players.values()) != self.agent.state.day):
                        return {cb.guarded(random.choice(self.agent.state.current_living_players)):1}
        return None
    # Vote for suspicious people.
    def vote(self):
        if self.agent.role != 'WEREWOLF' and self.agent.role != 'POSSESSED': return None
        if self.fake_guilty and self.fake_guilty in self.agent.state.current_living_players:
            return {self.fake_guilty:1}
        return None