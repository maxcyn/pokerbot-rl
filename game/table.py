class Table:
    def __init__(self, players):
        self.players = players
        self.community_cards = []
        self.pot = 0
    def reset(self):
        self.community_cards = []
        self.pot = 0
        for p in self.players:
            p.reset()
