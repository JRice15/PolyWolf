from policies.base_agenda import Agenda
from aiwolfpy import contentbuilder as cb

# Agent prioritizes killing people who might be the bodyguard, or sharing identities of saved people if you are a bodyguard.
class BodyguardPriority(Agenda):
    def __init__(self, agent):
        super().__init__(agent)
        self.weights['attack'] = 0.25
        self.weights['talk'] = 2
        self.last_claimed = None
        self.last_shared = None
    def reset(self):
        self.last_claimed = None
        self.last_shared = None
    # The bodyguard must die!
    def attack(self):
        if type(self.agent.estimator.predictions) == type(None): return None
        bg_probabilities = self.agent.estimator.predictions[:,0] # Column 0 = Bodyguard predictions
        bg_probabilities = {player_id:bg_probabilities[player_id-1] for player_id in self.agent.state.current_living_players}
        return bg_probabilities
    # If you prevented somebody from dying, they are confirmed not-werewolf, so share that result!
    def talk(self):
        if self.agent.role == 'BODYGUARD':
            if self.agent.target in self.agent.state.confirmed.keys():
                if self.last_claimed != self.agent.state.day:
                    self.last_claimed = self.agent.state.day
                    return {cb.comingout(self.agent.id, 'BODYGUARD'):1}
                if self.last_shared != self.agent.state.day:
                    self.last_shared = self.agent.state.day
                    return {cb.guarded(self.agent.target):1}
        return None