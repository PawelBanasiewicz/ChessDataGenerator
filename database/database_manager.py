import sqlite3

from utils.constants import GENERATED_DATA_DATABASE_PATH


class DatabaseManager:

    def __init__(self, database_paths):
        self.connections = {}
        for database_name in database_paths:
            connection = sqlite3.connect(database_name)
            self.connections[database_name] = connection
        self.cursors = {database_name: connection.cursor() for database_name, connection in self.connections.items()}
        self.create_players_table_if_not_exists(GENERATED_DATA_DATABASE_PATH)
        self.create_games_table_if_not_exists(GENERATED_DATA_DATABASE_PATH)

    def create_players_table_if_not_exists(self, database_path):
        cursor = self.cursors.get(database_path)
        if cursor:
            cursor.execute('''
                       CREATE TABLE IF NOT EXISTS players (
                           player_id INTEGER PRIMARY KEY,
                           first_name TEXT,
                           last_name TEXT,
                           birth_date DATE,
                           sex TEXT,
                           elo_rating INTEGER
                       )
                   ''')
            cursor.connection.commit()

    def create_games_table_if_not_exists(self, database_path):
        cursor = self.cursors.get(database_path)
        if cursor:
            cursor.execute('''
                        CREATE TABLE IF NOT EXISTS games (
                            game_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            opening_id INTEGER,
                            player1_id INTEGER,
                            player2_id INTEGER,
                            pgn TEXT,
                            result VARCHAR(10),
                            moves_number INTEGER,
                            date DATE,
                            FOREIGN KEY (opening_id) REFERENCES openings (opening_id),
                            FOREIGN KEY (player1_id) REFERENCES players (player_id),
                            FOREIGN KEY (player2_id) REFERENCES players (player_id)
                        )
                    ''')
            cursor.connection.commit()

    def insert_players(self, database_path, players):
        cursor = self.cursors.get(database_path)
        for player in players:
            sql = "INSERT INTO players (first_name, last_name, birth_date, sex, elo_rating) VALUES (?, ?, ?, ?, ?)"
            cursor.execute(sql, (player.first_name, player.last_name, player.birth_date, player.sex, player.elo_rating))
        cursor.connection.commit()

    def insert_games(self, database_path, games):
        cursor = self.cursors.get(database_path)
        for game in games:
            date_without_time = game.date.date()
            cursor.execute('''
                INSERT INTO games (opening_id, player1_id, player2_id, pgn, result, moves_number, date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (game.opening_code, game.player1_id, game.player2_id, game.pgn, game.result, game.moves_number,
                  date_without_time))
            cursor.connection.commit()

    def generate_query_to_insert_players_to_mysql(self, database_path, output_file_path):
        cursor = self.cursors.get(database_path)
        cursor.execute("SELECT first_name, last_name, birth_date, sex, elo_rating FROM players")
        players = cursor.fetchall()

        line_last_char = ','
        with open(output_file_path, "w") as file:
            file.write("INSERT INTO Players (first_name, last_name, birth_date, sex, elo_rating)\nVALUES\n")
            for i, player in enumerate(players):
                first_name, last_name, birth_date, sex, elo_rating = player
                if i == len(players) - 1:
                    line_last_char = ';'
                file.write(f"('{first_name}', '{last_name}', '{birth_date}', '{sex}', "
                           f"{elo_rating}){line_last_char}\n")

    def generate_query_to_insert_games_to_mysql(self, database_path, output_file_path):
        cursor = self.cursors.get(database_path)
        cursor.execute("""
            SELECT opening_id, player1_id, player2_id, pgn, result, moves_number, date 
            FROM games
        """)
        games = cursor.fetchall()

        line_last_char = ','
        with open(output_file_path, "w") as file:
            file.write(
                "INSERT INTO games (opening_id, player1_id, player2_id, pgn, result, moves_number, date)\nVALUES\n")
            for i, game in enumerate(games):
                opening_id, player1_id, player2_id, pgn, result, moves_number, date = game
                date = date.split()[0]
                if i == len(games) - 1:
                    line_last_char = ';'
                file.write(
                    f"({opening_id}, {player1_id}, {player2_id}, '{pgn}', '{result}', "
                    f"{moves_number}, '{date}'){line_last_char}\n")

    def close(self):
        for connection in self.connections.values():
            connection.close()
