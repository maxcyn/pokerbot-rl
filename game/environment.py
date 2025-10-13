# maxcyn/pokerbot-rl/pokerbot-rl-5d9393068a13f17d65d069dc7abc424945cc334b/game/environment.py
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
        
        self.current_player_index = (bb_pos + 1) % len(self.players)
        self.last_raiser_index = bb_pos
        
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
        self.current_player_index = (self.dealer_button_pos + 1) % len(self.players)
        self.last_raiser_index = -1

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
            scores.sort(key=lambda x: x[1])
            return scores[0][0]

    def step(self, action):
        p = self.players[self.current_player_index]
        opponent = self.players[(self.current_player_index + 1) % len(self.players)]
        reward = 0

        # Action logic
        if action == 0: # Fold
            p.folded = True
        elif action == 1: # Call/Check
            amount_to_call = opponent.current_bet - p.current_bet
            p.bet(amount_to_call)
        elif action in [2, 3, 4, 5]: # Raise actions
            min_raise = opponent.current_bet * 2
            amount_to_raise = get_raise_amount(action, min_raise, self.table.pot, p.chips)
            total_bet_amount = amount_to_raise + (opponent.current_bet - p.current_bet)
            p.bet(total_bet_amount)
            self.last_raiser_index = self.current_player_index

        # Update pot based on all player bets
        self.table.pot = sum(player.current_bet for player in self.players)
        
        # Check for end of betting round or end of hand
        betting_round_over = False
        active_players = [p for p in self.players if not p.folded]
        if len(active_players) <= 1:
            self.done = True
        else:
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            action_is_closed = (self.last_raiser_index != -1 and self.players[self.last_raiser_index].current_bet == p.current_bet) or \
                               (self.last_raiser_index == -1 and self.players[0].current_bet == self.players[1].current_bet and p.current_bet > 0)

            if action_is_closed:
                 betting_round_over = True

        if betting_round_over:
            self._advance_round()

        if self.done:
            winner = self._determine_winner()
            winner.chips += self.table.pot
            self.table.pot = 0
            
            dqn_player = self.players[0]
            reward = dqn_player.chips - dqn_player.starting_chips
            
        return self.get_state(), reward, self.done