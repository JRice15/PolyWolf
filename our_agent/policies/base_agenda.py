# A modular representation of a particular behavior or piece of policy.
# Combined in linear combinations with other agendas.
from collections import defaultdict

class Agenda:
    def __init__(self, agent):
        self.agent = agent
        self.state = agent.state
        self.weights = defaultdict(int)
    def reset(self):
        return
    def talk(self):
        return None
    def vote(self):
        return None
    def attack(self):
        return None
    def protect(self):
        return None
    def scan(self):
        return None