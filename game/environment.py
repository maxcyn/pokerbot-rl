from .deck import Deck
from .table import Table
from .hand_evaluator import evaluate_hand

class BettingRound:
    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3
    SHOWDOWN = 4

def get_raise_amount(action, min_raise, pot, player_chips):
    if action == 2:  # Min-raise
        return min(min_raise, player_chips)
    elif action == 3:  # Half-pot
        return min(int(0.5 * pot), player_chips)
    elif action == 4:  # Pot-size
        return min(pot, player_chips)
    elif action == 5: # All-in
        return player_chips
    return 0

class PokerEnvironment:
    def __init__(self, players, blinds=(10, 20)):
        self.players = players
        self.small_blind, self.big_blind = blinds
        self.deck = Deck()
        self.table = None
        self.dealer_button_pos = -1
        self.current_player_index = 0
        self.betting_round = BettingRound.PREFLOP
        self.last_raiser_index = -1
        self.done = False

    def _get_player_positions(self):
        sb_pos = (self.dealer_button_pos + 1) % len(self.players)
        bb_pos = (self.dealer_button_pos + 2) % len(self.players)
        return sb_pos, bb_pos

    def reset(self):
        self.deck = Deck()
        self.deck.shuffle()
        self.dealer_button_pos = (self.dealer_button_pos + 1) % len(self.players)
        
        for p in self.players:
            p.reset_hand()
            p.hand = self.deck.deal(2)
        
        self.table = Table(self.players)
        self.betting_round = BettingRound.PREFLOP
        self.done = False

        sb_pos, bb_pos = self._get_player_positions()
        sb_player = self.players[sb_pos]
        bb_player = self.players[bb_pos]

        sb_amount = sb_player.post_blind(self.small_blind)
        bb_amount = bb_player.post_blind(self.big_blind)
        self.table.pot += sb_amount + bb_amount
        
        # In heads-up, SB/Button acts first pre-flop
        self.current_player_index = sb_pos
        self.last_raiser_index = bb_pos # The BB is the "last raise"
        
        return self.get_state()

    def get_state(self):
        p = self.players[self.current_player_index]
        opponent = self.players[(self.current_player_index + 1) % len(self.players)]
        return {
            'hand': p.hand, 'community': self.table.community_cards,
            'chips': p.chips, 'pot': self.table.pot,
            'current_bet': p.current_bet, 'opponent_chips': opponent.chips,
            'opponent_bet': opponent.current_bet, 'position': self.current_player_index,
            'betting_round': self.betting_round
        }

    def _start_new_betting_round(self):
        for p in self.players:
            p.current_bet = 0
        # Post-flop, SB/Button always acts first
        self.current_player_index = (self.dealer_button_pos + 1) % len(self.players)
        self.last_raiser_index = -1 # No raiser yet

    def _advance_round(self):
        if self.betting_round == BettingRound.PREFLOP:
            self.betting_round = BettingRound.FLOP
            self.table.community_cards.extend(self.deck.deal(3))
        elif self.betting_round == BettingRound.FLOP:
            self.betting_round = BettingRound.TURN
            self.table.community_cards.extend(self.deck.deal(1))
        elif self.betting_round == BettingRound.TURN:
            self.betting_round = BettingRound.RIVER
            self.table.community_cards.extend(self.deck.deal(1))
        else:
            self.betting_round = BettingRound.SHOWDOWN
            self.done = True
        
        if not self.done:
            self._start_new_betting_round()

    def _determine_winner(self):
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) == 1:
            return active_players[0]
        else:
            scores = [(p, evaluate_hand(p.hand, self.table.community_cards)) for p in active_players]
            scores.sort(key=lambda x: x[1]) # Lower is better
            return scores[0][0]

    def step(self, action):
        p = self.players[self.current_player_index]
        opponent = self.players[(self.current_player_index + 1) % len(self.players)]
        reward = 0
        betting_round_over = False

        if p.is_all_in:
            # Player is all-in, they cannot act.
            action = 1 # Force a "check"

        if action == 0: # Fold
            p.folded = True
        
        elif action == 1: # Call/Check
            amount_to_call = opponent.current_bet - p.current_bet
            bet_amount = p.bet(amount_to_call)
            self.table.pot += bet_amount
            
            # If player called, the betting round is over (unless they were BB and SB just limped)
            if amount_to_call > 0 or self.betting_round > BettingRound.PREFLOP:
                 betting_round_over = True

        elif action in [2, 3, 4, 5]: # Raise
            min_raise = (opponent.current_bet - p.current_bet) + opponent.current_bet
            amount_to_raise = get_raise_amount(action, min_raise, self.table.pot, p.chips)
            
            # Calculate the total bet player needs to make
            # (call opponent's bet + the raise amount)
            amount_to_call = opponent.current_bet - p.current_bet
            total_bet_amount = amount_to_call + amount_to_raise
            
            bet_amount = p.bet(total_bet_amount)
            self.table.pot += bet_amount
            self.last_raiser_index = self.current_player_index

        # --- Check for end of hand/round ---
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) <= 1:
            self.done = True
        
        # If the round isn't over by a fold or call, move to the next player
        if not self.done and not betting_round_over:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            
            # If action gets back to the raiser, round is over
            if self.current_player_index == self.last_raiser_index:
                betting_round_over = True
                
        if betting_round_over and not self.done:
            self._advance_round()

        if self.done:
            winner = self._determine_winner()
            winner.chips += self.table.pot
            self.table.pot = 0
            
            dqn_player = self.players[0]
            reward = dqn_player.chips - dqn_player.starting_chips
            
        return self.get_state(), reward, self.done