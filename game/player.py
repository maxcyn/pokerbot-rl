class Player:
    def __init__(self, name, chips=1000):
        self.name = name
        self.chips = chips
        self.hand = []
        self.current_bet = 0
        self.folded = False
    def reset(self):
        self.hand = []
        self.current_bet = 0
        self.folded = False
