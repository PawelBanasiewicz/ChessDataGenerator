from database.database_manager import DatabaseManager
from generators.games_data_generator import GameDataGenerator
from utils.constants import GENERATED_DATA_DATABASE_PATH, GAMES_OUTPUT_PATH

if __name__ == '__main__':
    games_number = 400

    games_data_generator = GameDataGenerator()
    games_list = games_data_generator.generate_games_list(games_number)

    database_manager = DatabaseManager([GENERATED_DATA_DATABASE_PATH])
    database_manager.insert_games(GENERATED_DATA_DATABASE_PATH, games_list)
    database_manager.generate_query_to_insert_games_to_mysql(GENERATED_DATA_DATABASE_PATH, GAMES_OUTPUT_PATH)

    games_data_generator.close_connections()
    database_manager.close()

