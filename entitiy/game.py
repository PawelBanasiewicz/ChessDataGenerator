class Game:
    def __init__(self, opening_id, player1_id, player2_id, pgn, result, moves_number, date):
        self.opening_code = opening_id
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.pgn = pgn
        self.result = result
        self.moves_number = moves_number
        self.date = date
