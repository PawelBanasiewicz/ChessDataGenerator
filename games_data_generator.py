import random
from datetime import datetime, timedelta

import chess
import chess.engine
import chess.pgn
from faker import Faker

from constants import CHESS_OPENINGS_DATABASE_PATH, \
    GENERATED_DATA_DATABASE_PATH, STOCKFISH_LINUX_PATH
from database_manager import DatabaseManager
from game import Game


class GameDataGenerator:
    def __init__(self):
        self.faker = Faker()
        self.database_manager = DatabaseManager([CHESS_OPENINGS_DATABASE_PATH, GENERATED_DATA_DATABASE_PATH])
        self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_LINUX_PATH, timeout=60)

    def generate_games_list(self, games_number):
        games = []
        for i in range(games_number):
            game = self.generate_game()
            games.append(game)

            formatted_date = game.date.strftime("%Y-%m-%d")

            self.database_manager.cursors.get(GENERATED_DATA_DATABASE_PATH).execute(
                "INSERT INTO games (opening_id, player1_id, player2_id, pgn, result, moves_number, date) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                [game.opening_id, game.player1_id, game.player2_id, game.pgn, game.result, game.moves_number,
                 formatted_date])

            self.database_manager.connections.get(GENERATED_DATA_DATABASE_PATH).commit()
            if i % 30:
                print(i)

    def generate_game(self):
        player1data, player2data = self.find_right_players(GENERATED_DATA_DATABASE_PATH)
        date = None

        if player1data and player2data:
            date = self.generate_random_game_date(player1data[3], player2data[3])

        game = chess.pgn.Game()
        game.headers["Event"] = self.faker.catch_phrase()
        game.headers["Site"] = self.faker.domain_word() + "chess.com"
        game.headers["Date"] = date.strftime("%Y.%m.%d")
        game.headers["Round"] = str(random.randint(1, 12))
        game.headers["White"] = player1data[1] + ' ' + player1data[2]
        game.headers["Black"] = player2data[1] + ' ' + player2data[2]

        opening_id, opening_moves = self.get_random_opening(CHESS_OPENINGS_DATABASE_PATH)
        uci_moves = opening_moves.split()

        board = chess.Board()

        for uci_move in uci_moves:
            move = chess.Move.from_uci(uci_move)
            board.push(move)
            game.add_variation(move)

        while not board.is_game_over():
            result = self.engine.play(board, chess.engine.Limit(time=0.1))
            move = result.move
            board.push(move)
            game.add_variation(move)
            uci_move = board.uci(move)
            uci_moves.append(uci_move)

        result = board.result()
        pgn_moves, moves_number = self.convert_uci_to_pgn_and_count_move_number(uci_moves)

        # opening_code = self.get_opening_code_from_pgn(CHESS_OPENINGS_DATABASE_PATH, pgn_moves)

        return Game(opening_id, player1data[0], player2data[0], pgn_moves, result, moves_number, date)

    def find_right_players(self, database_path):
        cursor = self.database_manager.connections.get(database_path).cursor()

        cursor.execute("SELECT * FROM players "
                       "ORDER BY RANDOM() "
                       "LIMIT 1")
        player1data = cursor.fetchone()

        if player1data:
            birth_date = datetime.strptime(player1data[3], "%Y-%m-%d")
            max_birth_date = birth_date - timedelta(days=80 * 365)

            cursor.execute("SELECT * FROM players "
                           "WHERE birth_date BETWEEN ? AND ? "
                           "AND player_id != ? "
                           "ORDER BY RANDOM() "
                           "LIMIT 1",
                           (max_birth_date, birth_date, player1data[0]))
            player2data = cursor.fetchone()

            if player2data:
                return player1data, player2data

        return None, None

    def get_random_opening(self, database_path):
        cursor = self.database_manager.connections.get(database_path).cursor()
        cursor.execute('SELECT opening_id, uci_moves FROM Openings ORDER BY RANDOM() LIMIT 1')
        result = cursor.fetchone()

        if result:
            opening_code = result[0]
            opening_moves = result[1]
        else:
            opening_code = None
            opening_moves = ""

        return opening_code, opening_moves

    @staticmethod
    def convert_uci_to_pgn_and_count_move_number(uci_moves):
        board = chess.Board()
        pgn_moves = ""
        move_number = 0

        for uci_move in uci_moves:
            move = chess.Move.from_uci(uci_move)
            san_move = board.san(move)
            if board.turn == chess.WHITE:
                move_number += 1
                pgn_moves += f"{move_number}. {san_move} "
            else:
                pgn_moves += san_move + " "
            board.push(move)

        return pgn_moves.strip(), move_number

    @staticmethod
    def generate_random_game_date(player1_birth_date, player2_birth_date):
        player1_birth_date = datetime.strptime(player1_birth_date, "%Y-%m-%d")
        player2_birth_date = datetime.strptime(player2_birth_date, "%Y-%m-%d")

        if player1_birth_date > player2_birth_date:
            younger = player1_birth_date
            difference = int((player1_birth_date - player2_birth_date).days / 365)
        else:
            younger = player2_birth_date
            difference = int((player2_birth_date - player1_birth_date).days / 365)

        max_year = younger.year + (90 - difference)
        min_year = younger.year + 7

        current_year = datetime.now().year

        if max_year > current_year:
            random_year = random.randint(min_year, current_year)
            min_date = datetime(random_year, 1, 1)
            max_date = datetime(random_year, datetime.now().month, datetime.now().day)
        else:
            random_year = random.randint(min_year, max_year)
            min_date = datetime(random_year, 1, 1)
            max_date = datetime(random_year, 12, 31)

        random_date = min_date + timedelta(days=random.randint(0, (max_date - min_date).days))

        return random_date

    def get_opening_code_from_pgn(self, database_path, pgn_moves):
        cursor = self.database_manager.connections.get(database_path).cursor()

        cursor.execute(
            'SELECT opening_id, pgn_moves FROM Openings WHERE ? '
            'LIKE "%" || pgn_moves || "%" ORDER BY LENGTH(pgn_moves) DESC', (pgn_moves,))
        result = cursor.fetchone()

        if result:
            opening_code = result[0]
        else:
            opening_code = None

        return opening_code

    def close_connections(self):
        self.database_manager.close()
        self.engine.close()
