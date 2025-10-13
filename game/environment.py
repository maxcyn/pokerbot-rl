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
        self.current_player_index = 0
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
        self.current_player_index = 0
        return self.get_state()

    def get_state(self):
        p = self.players[self.current_player_index]
        opponent = self.players[(self.current_player_index + 1) % len(self.players)]
        state = {
            'hand': p.hand,
            'community': self.table.community_cards,
            'chips': p.chips,
            'pot': self.table.pot,
            'current_bet': p.current_bet,
            'opponent_chips': opponent.chips,
            'opponent_bet': opponent.current_bet,
            'position': self.current_player_index
        }
        return state

    def step(self, action):
        p = self.players[self.current_player_index]
        if action == 0:
            p.folded = True
        elif action == 1:
            # Basic call/check logic
            to_call = self.players[(self.current_player_index + 1) % len(self.players)].current_bet - p.current_bet
            amount = min(to_call, p.chips)
            p.chips -= amount
            p.current_bet += amount
            self.table.pot += amount
        elif action in [2, 3, 4, 5]:
            min_raise = 10 # placeholder
            amount = get_raise_amount(action, min_raise, self.table.pot, p.chips)
            p.chips -= amount
            p.current_bet += amount
            self.table.pot += amount

        # Switch player
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

        # End condition
        if sum(not pl.folded for pl in self.players) == 1 or len(self.table.community_cards) == 5:
            self.done = True
        
        reward = self.get_reward()
        
        return self.get_state(), reward, self.done

    def get_reward(self):
        if not self.done:
            return 0
        
        scores = [evaluate_hand(p.hand, self.table.community_cards) if not p.folded else float('inf') for p in self.players]
        winner_index = scores.index(min(scores))
        
        # Simple reward: winner gets the pot, loser loses their bet
        for i, p in enumerate(self.players):
            if i == winner_index:
                return self.table.pot - p.current_bet
            else:
                return -p.current_bet