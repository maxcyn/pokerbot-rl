from .deck import Deck
from .table import Table
from .hand_evaluator import evaluate_hand

def get_raise_amount(action, min_raise, pot, player_chips):
    if action == 2:  # Min-raise
        return min(min_raise, player_chips)
    elif action == 3:  # Half-pot
        return min(int(0.5 * pot), player_chips)
    elif action == 4:  # Pot-size
        return min(pot, player_chips)
    elif action == 5:  # All-in
        return player_chips
    else:
        return 0

class PokerEnvironment:
    def __init__(self, players):
        self.players = players
        self.deck = Deck()
        self.table = None
        self.current_player = 0
        self.done = False

    def reset(self):
        self.deck = Deck()
        self.deck.shuffle()
        for p in self.players:
            p.reset()
            p.hand = self.deck.deal(2)
        self.table = Table(self.players)
        self.table.community_cards = self.deck.deal(3)  # Flop
        self.done = False
        self.current_player = 0
        return self.get_state()
    
    def get_state(self):
        # Return a simple state: player hand, community cards, chips, pot
        p = self.players[self.current_player]
        state = {
            'hand': p.hand,
            'community': self.table.community_cards,
            'chips': p.chips,
            'pot': self.table.pot
        }
        return state
        
    def step(self, action):
        # action: 0=fold, 1=call/check, 2=raise
        p = self.players[self.current_player]
        if action == 0:
            p.folded = True
        elif action == 1:
            pass  # call/check logic
        elif action in [2, 3, 4, 5]:
            min_raise = 10 # placeholder for min raise
            amount = get_raise_amount(action, min_raise, self.table.pot, p.chips)
            p.chips -= amount
            self.table.pot += amount
        # Switch player
        self.current_player = (self.current_player + 1) % len(self.players)
        # End condition: one left or after river
        if sum(not pl.folded for pl in self.players) == 1 or len(self.table.community_cards) == 5: # game ends if there is 1 person left or after river
            self.done = True
        return self.get_state(), self.get_reward(), self.done
    
    def get_reward(self):
        # Simple reward: +1 for winner, -1 for loser
        if not self.done:
            return 0
        # Find winner
        scores = [evaluate_hand(p.hand, self.table.community_cards) if not p.folded else float('inf') for p in self.players]
        winner = scores.index(min(scores))
        rewards = [1 if i == winner else -1 for i in range(len(self.players))]
        return rewards[self.current_player]