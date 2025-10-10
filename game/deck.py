import random
from .card import Card

class Deck:
    def __init__(self):
        self.cards = [Card(s, r) for s in Card.SUITS for r in Card.RANKS]
    def shuffle(self):
        random.shuffle(self.cards)
    def deal(self, num):
        dealt = self.cards[:num]
        self.cards = self.cards[num:]
        return dealt