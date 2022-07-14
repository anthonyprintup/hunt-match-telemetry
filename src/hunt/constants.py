import os.path

HUNT_SHOWDOWN_APP_ID: int = 594650  # Hunt: Showdown App ID
HUNT_SHOWDOWN_TEST_SERVER_APP_ID: int = 770720  # Hunt: Showdown (Test Server) App ID

# The path (directory) to where match logs are stored
WORKING_DIRECTORY: str = os.getcwd()
RESOURCES_PATH: str = os.path.realpath(os.path.join(WORKING_DIRECTORY, "resources"))
MATCH_LOGS_PATH: str = os.path.join(RESOURCES_PATH, "logs")

# Steam
STEAMWORKS_BINARIES_PATH: str = os.path.join(RESOURCES_PATH, "steam")
STEAMWORKS_SDK_PATH: str = os.path.join(STEAMWORKS_BINARIES_PATH, "steamworks_sdk.zip")

# Formatting
STAR_SYMBOL: str = "★"
MMR_RANGES: tuple[int, ...] = (0, 2000, 2300, 2600, 2750, 3000)

# Database
DATABASE_PATH: str = os.path.join(RESOURCES_PATH, "match_data.db")
DATABASE_TEST_SERVER_PATH: str = os.path.join(RESOURCES_PATH, "match_data_ts.db")


# Helper function to generate create table queries
def _create_table_helper(table_name: str, fields: tuple[str, ...]) -> str:
    return f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(fields)})"


# Tables
_PLAYER_LOG_COLUMNS: tuple[str, ...] = ("id INTEGER PRIMARY KEY",
                                        "profile_id INTEGER UNIQUE",
                                        "name TEXT NOT NULL", "mmr INTEGER DEFAULT 0 NOT NULL",
                                        "kills INTEGER DEFAULT 0 NOT NULL", "deaths INTEGER DEFAULT 0 NOT NULL",
                                        "encounters INTEGER DEFAULT 0 NOT NULL")
DATABASE_TABLE_QUERIES: tuple[str, ...] = (
    _create_table_helper("data_hashes", ("id INTEGER PRIMARY KEY", "hash varchar(64) UNIQUE", "path TEXT NOT NULL")),
    _create_table_helper("player_log_bountyhunt", _PLAYER_LOG_COLUMNS),
    _create_table_helper("player_log_quickplay", _PLAYER_LOG_COLUMNS))
