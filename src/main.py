import sys
import time
import os.path
import logging
from functools import partial
from contextlib import closing

from colorama import Fore, Style

from src.hunt.utilities.hunt import fetch_hunt_attributes_path, format_mmr
from src.hunt.utilities.file_watcher import FileWatchdog
from src.hunt.attributes_parser import ElementTree, Match, Player, parse_match
from src.hunt.constants import DATABASE_PATH
from src.hunt.utilities.database import Database


def main():
    # Setup logging
    logging.basicConfig(format="[%(asctime)s, %(levelname)s] %(message)s",
                        datefmt="%H:%M", level=logging.INFO, stream=sys.stdout)

    # Locate the attributes file
    attributes_path: str = fetch_hunt_attributes_path()
    assert os.path.exists(attributes_path), "Attributes file does not exist."

    database: Database
    with closing(Database(file_path=DATABASE_PATH)) as database:
        # Set up a file watcher to listen for changes on the attributes file
        file_watchdog: FileWatchdog = FileWatchdog(file_path=attributes_path,
                                                   callback=partial(attributes_file_modified, database=database))
        file_watchdog.start()

        # Inform the user that the program has started
        logging.info("Watching for matches, good luck and have fun!")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            # Stop the file watcher if a keyboard interrupt is received
            file_watchdog.stop()
        file_watchdog.join()

    # Signal to the user that we're shutting down
    logging.info("Shutting down.")


def attributes_file_modified(file_path: str, database: Database):
    try:
        # Attempt to parse the attributes file;
        #  when the file is being written to by the game
        #  it usually has a step where it contains garbage
        #  data (empty?), which will throw an exception.
        parsed_attributes: ElementTree = ElementTree.parse(source=file_path)
    except ElementTree.ParseError as exception:
        # Skip the update
        logging.debug(f"Failed to parse the attributes file: {exception=}")
        return

    # Parse the teams from the attributes file
    try:
        match: Match = parse_match(root=parsed_attributes.getroot())
    except (AttributeError, AssertionError) as exception:
        logging.debug(f"Failed to parse the attributes file: {exception=}")
        return

    # Save match data to disk
    if match.try_save_to_file(database=database):
        return  # Skip printing an already existing entry

    # Print useful data from the match
    log_player_data(match)


def log_player_data(match: Match):
    """
    Logs the user's MMR, the players they were killed by,
      and the players they killed.
    :param match: a parsed Match instance
    """
    players: tuple[Player] = tuple(player for team in match.teams for player in team.players)
    players_killed: tuple[Player] = tuple(filter(lambda player: player.killed_by_me, players))
    players_killed_me: tuple[Player] = tuple(filter(lambda player: player.killed_me, players))

    user: Player | None = None
    try:
        user = next(filter(lambda player: player.name == match.player_name, players), None)
    except RuntimeError as exception:
        logging.warning("Failed to locate the user by their username.")
        logging.debug(f"Failed to fetch the user's Steam username: {exception=}")

    # Print the user's MMR
    if user:
        logging.info(f"User MMR: {format_mmr(user.mmr)}")
    player: Player
    for player in players_killed:
        kill_count: str = f" {player.killed_by_me}x" if player.killed_by_me > 1 else ""
        logging.info(f"  Killed {Fore.GREEN}{player.name}{Style.RESET_ALL} ({format_mmr(player.mmr)}){kill_count}")
    for player in players_killed_me:
        death_count: str = f" {player.killed_me}x" if player.killed_me > 1 else ""
        logging.info(f"  Killed {Fore.RED}{player.name}{Style.RESET_ALL} ({format_mmr(player.mmr)}){death_count}")


if __name__ == "__main__":
    main()
