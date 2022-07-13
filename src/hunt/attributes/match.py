import json
import os.path
from hashlib import sha256
from datetime import datetime
from dataclasses import dataclass

from .accolade import Accolade
from .entry import Entry
from .rewards import Rewards
from .team import Team, Player
from ..constants import MATCH_LOGS_PATH
from ..database.queries import DatabaseClient, data_hash_exists, insert_match_hash, update_player_data


@dataclass(frozen=True)
class Match:
    player_name: str
    hunter_survived: bool
    is_quickplay: bool
    accolades: tuple[Accolade, ...]
    entries: tuple[Entry, ...]
    rewards: Rewards
    teams: tuple[Team, ...]

    def _generate_file_path(self) -> str:
        """
        Generates a file path for the match.
        :return: the file path for the match data
        """
        now: datetime = datetime.now()
        return os.path.join(MATCH_LOGS_PATH,
                            f"{now.year}-{now.month:02d}-{now.day:02d}",
                            f"{'quickplay' if self.is_quickplay else 'bounty_hunt'}",
                            f"{now.hour:02d}-{now.minute:02d}-{now.second:02d}.json")

    def try_save_to_file(self, database: DatabaseClient) -> bool:
        """
        Converts the match data to json and saves it to the file path,
          if the match data hasn't already been saved.
        :param database: a DatabaseClient instance
        :return: True if this entry already exists in the database, otherwise False.
        """
        # Generate the match data and its hash
        match_data: str = json.dumps(self, indent=2, default=vars)
        match_hash: str = sha256(match_data.encode()).hexdigest()

        # Check if the hash already exists in the database to prevent duplicates
        if data_hash_exists(database, match_hash=match_hash):
            return True

        # Generate the file path
        generated_file_path: str = self._generate_file_path()

        # Save the hash to the database
        insert_match_hash(database, match_hash=match_hash, file_path=generated_file_path)

        # Update the player log
        player: Player
        for player in (player for team in self.teams for player in team.players):
            update_player_data(database, profile_id=player.profile_id, name=player.name, mmr=player.mmr,
                               kills=player.killed_by_me, deaths=player.killed_me, is_quickplay=self.is_quickplay)

        # Create the directories
        directory_path: str = os.path.dirname(generated_file_path)
        os.makedirs(name=directory_path, exist_ok=True)

        # Save the data to a file
        with open(self._generate_file_path(), mode="w") as file:
            file.write(match_data)
        return False
