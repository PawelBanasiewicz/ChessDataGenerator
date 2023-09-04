import random
from faker import Faker
from entitiy.player import Player


class PlayerDataGenerator:
    def __init__(self):
        self.fake = Faker()

    def generate_player_data(self):
        sex = random.choice(['M', 'F'])

        if sex == 'M':
            first_name = self.fake.first_name_male()
        else:
            first_name = self.fake.first_name_female()

        last_name = self.fake.last_name()
        birth_date = self.fake.date_of_birth(minimum_age=13, maximum_age=323)
        elo_rating = random.randint(650, 2850)

        return Player(first_name, last_name, birth_date, sex, elo_rating)

    def generate_players_list(self, players_numbers):
        players = []
        for _ in range(players_numbers):
            player = self.generate_player_data()
            players.append(player)
        return players
