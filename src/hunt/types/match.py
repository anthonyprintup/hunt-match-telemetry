import json
import os.path
from hashlib import sha256
from datetime import datetime
from contextlib import closing
from dataclasses import dataclass

from .entry import Entry
from .team import Team
from ..constants import RESOURCES_PATH, HASH_TABLE_NAME
from ..utilities.database import Database, Cursor


@dataclass(frozen=True)
class Match:
    player_name: str
    hunter_survived: bool
    is_quickplay: bool
    entries: tuple[Entry]
    teams: tuple[Team]

    @staticmethod
    def _hash_exists_in_database(database: Database, match_hash: str) -> bool:
        cursor: Cursor
        with closing(database.cursor()) as cursor:
            query: str = f"SELECT EXISTS(SELECT 1 FROM {HASH_TABLE_NAME} WHERE hash=?)"
            return cursor.execute(query, (match_hash,)).fetchone()[0] >= 1

    def _save_hash_to_database(self, database: Database, match_hash: str):
        cursor: Cursor
        with closing(database.cursor()) as cursor:
            cursor.execute(f"INSERT INTO {HASH_TABLE_NAME}(hash, quickplay) VALUES (?, ?)",
                           (match_hash, self.is_quickplay))
        database.save()

    def _generate_file_path(self) -> str:
        now: datetime = datetime.now()
        return os.path.join(RESOURCES_PATH,
                            f"{now.year}-{now.month:02d}-{now.day:02d}",
                            f"{'quickplay' if self.is_quickplay else 'bounty_hunt'}",
                            f"{now.hour:02d}-{now.minute:02d}-{now.second:02d}.json")

    def try_save_to_file(self, database: Database) -> bool:
        """
        Converts the match data to json and saves it to the file path,
          if the match data hasn't already been saved.
        :return: True if this entry already exists in the database, otherwise False.
        """
        # Generate the match data and its hash
        match_data: str = json.dumps(self, indent=2, default=vars)
        match_hash: str = sha256(match_data.encode()).hexdigest()

        # Check if the hash already exists in the database to prevent duplicates
        if self._hash_exists_in_database(database, match_hash=match_hash):
            return True

        # Save the hash to the database
        self._save_hash_to_database(database, match_hash=match_hash)

        # Save the data to a file
        generated_file_path: str = self._generate_file_path()

        # Create the directories
        directory_path: str = os.path.dirname(generated_file_path)
        os.makedirs(name=directory_path, exist_ok=True)

        with open(self._generate_file_path(), mode="w") as file:
            file.write(match_data)
        return False
