import os.path

HUNT_SHOWDOWN_STEAM_ID: int = 594650  # Hunt: Showdown Steam ID

# The path (directory) to where match logs are stored
WORKING_DIRECTORY: str = os.getcwd()
RESOURCES_PATH: str = os.path.realpath(os.path.join(WORKING_DIRECTORY, "resources"))
os.makedirs(name=RESOURCES_PATH, exist_ok=True)  # Create the resource directory if it doesn't exist

# Steam
STEAMWORKS_BINARIES_PATH: str = os.path.join(RESOURCES_PATH, "steam")
STEAMWORKS_SDK_PATH: str = os.path.join(STEAMWORKS_BINARIES_PATH, "steamworks_sdk.zip")
os.makedirs(name=STEAMWORKS_BINARIES_PATH, exist_ok=True)  # Create the bin directory if it doesn't exist

# Formatting
STAR_SYMBOL: str = "★"
MMR_RANGES: tuple[int, ...] = (0, 2000, 2300, 2600, 2750, 3000)

# Database
DATABASE_PATH: str = os.path.join(RESOURCES_PATH, "match_data.db")


# Helper function to generate create table queries
def _create_table_helper(table_name: str, fields: tuple[str, ...]) -> str:
    return f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(fields)})"


# Tables
_PLAYER_LOG_COLUMNS = ("id INTEGER PRIMARY KEY",
                       "profile_id INTEGER UNIQUE", "name TEXT NOT NULL", "mmr INTEGER DEFAULT 0 NOT NULL",
                       "kills INTEGER DEFAULT 0 NOT NULL", "deaths INTEGER DEFAULT 0 NOT NULL",
                       "encounters INTEGER DEFAULT 0 NOT NULL")
DATABASE_TABLE_QUERIES: tuple[str, ...] = (
    _create_table_helper("data_hashes", ("id INTEGER PRIMARY KEY", "hash varchar(64) UNIQUE", "path TEXT NOT NULL")),
    _create_table_helper("player_log_bountyhunt", _PLAYER_LOG_COLUMNS),
    _create_table_helper("player_log_quickplay", _PLAYER_LOG_COLUMNS)
)

# Entry categories
_BOSS_NAMES: tuple[str, ...] = ("assassin", "spider", "butcher", "scrapbeak")
BOUNTY_CATEGORIES: tuple[str, ...] = (
    "accolade_bad_luck",
    "accolade_clues_found",
    *(f"accolade_found_{boss_name}" for boss_name in _BOSS_NAMES),
    *(f"accolade_killed_{boss_name}" for boss_name in _BOSS_NAMES),
    *(f"accolade_contract_{boss_name}" for boss_name in _BOSS_NAMES),
    *(f"accolade_clean_sweep_{boss_name}" for boss_name in _BOSS_NAMES),
    "accolade_trophy_extraction_bonus",
    "accolade_quickplay_wellsprings_found"
)
