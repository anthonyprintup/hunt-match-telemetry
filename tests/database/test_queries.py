import random
import sqlite3
from hashlib import sha256
from contextlib import closing, nullcontext as does_not_raise

import pytest
from _pytest.python_api import RaisesContext

from hunt.database.client import Client as DatabaseClient, Cursor
from hunt.database.queries import data_hash_exists, insert_match_hash, update_player_data

# Global variables for data_hashes
_DUMMY_HASH: str = sha256(b"dummy").hexdigest()
_DUMMY_PATH: str = "/tmp/dummy.json"


@pytest.mark.order(-1)
@pytest.mark.parametrize("match_hash", (_DUMMY_HASH,))
def test_data_hash_exists(database_client: DatabaseClient, match_hash: str) -> None:
    """
    Test data_hash_exists by checking for a known (already inserted) hash value.
    :param database_client: a Database instance
    :param match_hash: the hash of the match
    """
    assert data_hash_exists(database_client, match_hash=match_hash)


@pytest.mark.parametrize("match_hash, file_path, context", (
        (_DUMMY_HASH, _DUMMY_PATH, does_not_raise()),
        (_DUMMY_HASH, _DUMMY_PATH, pytest.raises(sqlite3.IntegrityError))))
def test_insert_match_hash(database_client: DatabaseClient,
                           match_hash: str, file_path: str, context: does_not_raise | RaisesContext) -> None:
    """
    Test insert_match_hash by inserting a dummy hash into the database and querying it.
    :param database_client: a Database instance
    :param match_hash: the hash of the match
    :param file_path: the path of the file where the match data was saved to
    """
    # Insert a dummy hash into the database
    with context:
        insert_match_hash(database_client, match_hash=match_hash, file_path=file_path)

    # Check to see if the dummy hash and file path were inserted properly
    cursor: Cursor
    with closing(database_client.cursor()) as cursor:
        query: str = "SELECT path FROM data_hashes where hash = ?"
        assert cursor.execute(query, (match_hash,)).fetchone()[0] == file_path
    database_client.save()


def test_update_player_data(database_client: DatabaseClient) -> None:
    """
    Test update_player_data by inserting a player into the player log, updating it and verifying it.
    :param database_client: a Database instance
    """
    # Setup variables
    profile_id: int = int(abs(random.gauss(10**8, 10**10)))
    name: str = "Jerry"
    mmr: int = int(random.gauss(2695, 600))

    # Insert the data into the player log
    update_player_data(database_client, profile_id=profile_id, name=name, mmr=mmr,
                       kills=2, deaths=0, is_quickplay=False)

    # Verify that the data was inserted properly
    cursor: Cursor
    query: str
    with closing(database_client.cursor()) as cursor:
        query = "SELECT name, mmr, kills, deaths, encounters FROM player_log_bountyhunt WHERE profile_id = ?"
        assert cursor.execute(query, (profile_id,)).fetchone() == (name, mmr, 2, 0, 1)

    # Update the data
    name = "Tom"
    mmr = int(random.gauss(2695, 600))
    update_player_data(database_client, profile_id=profile_id, name=name, mmr=mmr,
                       kills=4, deaths=1, is_quickplay=False)

    # Verify that the data was updated properly
    with closing(database_client.cursor()) as cursor:
        query = "SELECT name, mmr, kills, deaths, encounters FROM player_log_bountyhunt WHERE profile_id = ?"
        assert cursor.execute(query, (profile_id,)).fetchone() == (name, mmr, 6, 1, 2)
