class Player:
    def __init__(self, name, chips=1000):
        self.name = name
        self.chips = chips
        self.starting_chips = chips
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.is_all_in = False

    def reset_hand(self):
        """Resets player's state for a new hand."""
        self.hand = []
        self.current_bet = 0
        self.folded = False
        self.is_all_in = False
        self.starting_chips = self.chips

    def reset_chips(self, chips):
        """Resets player's chips for a new game/match."""
        self.chips = chips

    def bet(self, amount):
        bet_amount = min(amount, self.chips)
        if bet_amount >= self.chips:
            self.is_all_in = True
        self.chips -= bet_amount
        self.current_bet += bet_amount
        return bet_amount

    def post_blind(self, amount):
        """Method for posting blinds, which is a forced bet."""
        return self.bet(amount)