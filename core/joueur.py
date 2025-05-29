
""""Player class"""
class Player:
    def __init__(self, player_id, symbol):
        self.id = player_id
        self.symbol = symbol
        self.score = 0

    def __str__(self):
        return f"Player {self.id} ({self.symbol})"