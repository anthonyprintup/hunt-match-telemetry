from contextlib import closing

from src.hunt.utilities.database import Database, Cursor


def match_hash_exists(database: Database, match_hash: str) -> bool:
    """
    Checks if a match hash already exists in the database
    :param database: a Database instance
    :param match_hash: the hash to check for
    :return: True if a hash is already in the database, otherwise False
    """
    cursor: Cursor
    with closing(database.cursor()) as cursor:
        query: str = "SELECT EXISTS(SELECT 1 FROM match_hashes WHERE hash = ?)"
        return cursor.execute(query, (match_hash,)).fetchone()[0] >= 1


def insert_match_hash(database: Database, match_hash: str, is_quickplay: bool):
    """
    Saves a match hash to the database.
    :param database: a Database instance
    :param match_hash: the hash to save
    :param is_quickplay: quickplay match indicator
    """
    cursor: Cursor
    with closing(database.cursor()) as cursor:
        query: str = "INSERT INTO match_hashes(hash, is_quickplay) VALUES (?, ?)"
        cursor.execute(query, (match_hash, is_quickplay))
    database.save()


def update_player_data(database: Database, profile_id: int, name: str, mmr: int, times_killed: int, times_died: int):
    """
    Inserts and updates a player's data in the database.
    :param database: a Database instance
    :param profile_id: the profile id of the player
    :param mmr: the current NNR of the player
    :param name: the name of the player
    :param times_killed: the times the player was killed by us
    :param times_died: the times we died to the player
    """
    cursor: Cursor
    with closing(database.cursor()) as cursor:
        # Insert the data if it doesn't exist
        insert_query: str = "INSERT OR IGNORE INTO player_log (profile_id, latest_name) VALUES (?, ?)"
        cursor.execute(insert_query, (profile_id, name))

        # Increase the times_killed and times_died values
        update_query: str = "UPDATE player_log SET latest_name = ?, latest_mmr = ?, " \
                            "times_killed = times_killed + ?, times_died = times_died + ? WHERE profile_id = ?"
        cursor.execute(update_query, (name, mmr, times_killed, times_died, profile_id))
    database.save()
