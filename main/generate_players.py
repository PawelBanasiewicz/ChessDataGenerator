from database.database_manager import DatabaseManager
from generators.player_data_generator import PlayerDataGenerator
from utils.constants import GENERATED_DATA_DATABASE_PATH, PLAYERS_OUTPUT_PATH

if __name__ == "__main__":
    players_number = 50_000

    PlayerDataGenerator = playerDataGenerator = PlayerDataGenerator()
    players_list = playerDataGenerator.generate_players_list(players_number)

    database_manager = DatabaseManager([GENERATED_DATA_DATABASE_PATH])
    database_manager.insert_players(GENERATED_DATA_DATABASE_PATH, players_list)
    database_manager.generate_query_to_insert_players_to_mysql(GENERATED_DATA_DATABASE_PATH, PLAYERS_OUTPUT_PATH)

    database_manager.close()
