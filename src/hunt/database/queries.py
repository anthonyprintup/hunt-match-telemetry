from contextlib import closing

from .client import Client as DatabaseClient, Cursor


def data_hash_exists(database: DatabaseClient, match_hash: str) -> bool:
    """
    Checks if a match hash already exists in the database
    :param database: a DatabaseClient instance
    :param match_hash: the hash to check for
    :return: True if a hash is already in the database, otherwise False
    """
    cursor: Cursor
    with closing(database.cursor()) as cursor:
        query: str = "SELECT EXISTS(SELECT 1 FROM data_hashes WHERE hash = ?)"
        return cursor.execute(query, (match_hash,)).fetchone()[0] >= 1


def insert_match_hash(database: DatabaseClient, match_hash: str, file_path: str) -> None:
    """
    Saves a match hash to the database.
    :param database: a DatabaseClient instance
    :param match_hash: the hash to save
    :param file_path: the path to the file
    """
    cursor: Cursor
    with closing(database.cursor()) as cursor:
        query: str = "INSERT INTO data_hashes (hash, path) VALUES (?, ?)"
        cursor.execute(query, (match_hash, file_path))
    database.save()


def update_player_data(database: DatabaseClient, profile_id: int, name: str, mmr: int,
                       kills: int, deaths: int, is_quickplay: bool) -> None:
    """
    Inserts and updates a player's data in the database.
    :param database: a DatabaseClient instance
    :param profile_id: the profile id of the player
    :param mmr: the current NNR of the player
    :param name: the name of the player
    :param kills: the amount of times the player was killed by us
    :param deaths: the amount of times we died to the player
    :param is_quickplay: True if the match was a quickplay match
    """
    # Construct the queries to execute (the strings are duplicated for easier code refactoring/highlighting)
    insert_query: str = "INSERT OR IGNORE INTO player_log_bountyhunt (profile_id, name) VALUES (?, ?)"
    update_query: str = "UPDATE player_log_bountyhunt SET name = ?, mmr = ?, " \
                        "kills = kills + ?, deaths = deaths + ?, " \
                        "encounters = encounters + 1 WHERE profile_id = ?"
    if is_quickplay:
        insert_query = "INSERT OR IGNORE INTO player_log_quickplay (profile_id, name) VALUES (?, ?)"
        update_query = "UPDATE player_log_quickplay SET name = ?, mmr = ?, " \
                       "kills = kills + ?, deaths = deaths + ?, " \
                       "encounters = encounters + 1 WHERE profile_id = ?"

    cursor: Cursor
    with closing(database.cursor()) as cursor:
        # Insert the data if it doesn't exist
        cursor.execute(insert_query, (profile_id, name))

        # Update all relevant values
        cursor.execute(update_query, (name, mmr, kills, deaths, profile_id))
    database.save()
