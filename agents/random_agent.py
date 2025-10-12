import random

class RandomAgent:
    def __init__(self, action_dim):
        self.action_dim = action_dim
    def select_action(self, state):
        return random.randint(0, self.action_dim - 1)