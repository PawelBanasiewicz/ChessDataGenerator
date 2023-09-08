from constants import GENERATED_DATA_DATABASE_PATH, GAMES_OUTPUT_PATH
from database_manager import DatabaseManager
from games_data_generator import GameDataGenerator

if __name__ == '__main__':
    games_number = 40

    games_data_generator = GameDataGenerator()
    games_list = games_data_generator.generate_games_list(games_number)

    database_manager = DatabaseManager([GENERATED_DATA_DATABASE_PATH])
    database_manager.insert_games(GENERATED_DATA_DATABASE_PATH, games_list)
    database_manager.generate_query_to_insert_games_to_mysql(GENERATED_DATA_DATABASE_PATH, GAMES_OUTPUT_PATH)

    games_data_generator.close_connections()
    database_manager.close()

