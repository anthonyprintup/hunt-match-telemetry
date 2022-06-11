import os.path

HUNT_SHOWDOWN_STEAM_ID: int = 594650  # Hunt: Showdown team ID (to locate the game's install path)

# The path (directory) to where match logs are stored
RESOURCES_PATH: str = os.path.realpath(os.path.join(os.path.dirname(__file__), r"../../resources"))
os.makedirs(name=RESOURCES_PATH, exist_ok=True)  # Create the resource directory if it doesn't exist

# Formatting
STAR_SYMBOL: str = "★"
MMR_RANGES: tuple[int, ...] = (0, 2000, 2300, 2600, 2750, 3000)

# Database
DATABASE_PATH: str = os.path.join(RESOURCES_PATH, "match_data.db")
HASH_TABLE_NAME: str = "match_hashes"
CREATE_TABLE_QUERY: str = f"CREATE TABLE if NOT EXISTS {HASH_TABLE_NAME}" \
                          f"(id INTEGER PRIMARY KEY, hash varchar(64) NOT NULL, quickplay BOOLEAN NOT NULL)"
