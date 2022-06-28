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
def create_table_helper(table_name: str, fields: tuple[str, ...]) -> str:
    return f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(fields)})"


# Tables
DATABASE_TABLE_QUERIES: tuple[str, ...] = (
    create_table_helper("data_hashes", ("id INTEGER PRIMARY KEY", "hash varchar(64) UNIQUE", "path TEXT NOT NULL")),
    create_table_helper("player_log", ("id INTEGER PRIMARY KEY", "profile_id INTEGER UNIQUE",
                                       "latest_name varchar(32) NOT NULL", "latest_mmr INTEGER DEFAULT 0 NOT NULL",
                                       "times_killed INTEGER DEFAULT 0 NOT NULL",
                                       "times_died INTEGER DEFAULT 0 NOT NULL",
                                       "times_seen INTEGER DEFAULT 0 NOT NULL"))
)
