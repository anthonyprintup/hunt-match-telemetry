import sys
import time
import os.path
import logging
from typing import Generator
from functools import partial

from colorama import Fore, Style

from hunt.constants import DATABASE_PATH, STEAMWORKS_SDK_PATH
from hunt.formats import format_mmr
from hunt.database.client import Client as DatabaseClient
from hunt.filesystem.watchdog import FileWatchdog
from hunt.steam.api import SteamworksApi, fetch_hunt_attributes_path, try_extract_steamworks_binaries
from hunt.attributes.parser import ElementTree, Match, Player, parse_match
from hunt.exceptions import SteamworksError, UnsupportedPlatformError, ParserError


def main():
    # Setup logging
    logging.basicConfig(format="[%(asctime)s, %(levelname)s] %(message)s",
                        datefmt="%H:%M", level=logging.INFO, stream=sys.stdout)

    try:
        # Extract the Steamworks binaries to disk
        steamworks_api_path: str = try_extract_steamworks_binaries()
    except SteamworksError as exception:
        logging.critical("Failed to extract the Steamworks binaries, are you missing the Steamworks SDK?")
        logging.info(f"The Steamworks SDK should be located at: {STEAMWORKS_SDK_PATH!r}")
        logging.debug(f"Steamworks error: {exception=}")
        return
    except UnsupportedPlatformError as exception:
        logging.critical("The current platform isn't supported.")
        logging.debug(f"Unsupported platform error: {exception=}")
        return

    try:
        # Initialize the Steamworks API
        steamworks_api: SteamworksApi = SteamworksApi.prepare_and_initialize(api_binary_path=steamworks_api_path)
    except SteamworksError as exception:
        logging.critical("A Steamworks API error occurred, is Steam running?")
        logging.debug(f"Steamworks error: {exception=}")
        return
    else:
        logging.info("Steamworks API initialized.")

    # Locate the attributes file
    attributes_path: str = fetch_hunt_attributes_path(steamworks_api)
    assert os.path.exists(attributes_path), "Attributes file does not exist."

    database: DatabaseClient
    with DatabaseClient(file_path=DATABASE_PATH) as database:
        # Set up a file watcher to listen for changes on the attributes file
        file_watchdog: FileWatchdog = FileWatchdog(
            file_path=attributes_path,
            callback=partial(attributes_file_modified, database=database, steamworks_api=steamworks_api))
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

    # Cleanup/shutdown the Steamworks API
    steamworks_api.shutdown()

    # Signal to the user that we're shutting down
    logging.info("Shutting down.")


def attributes_file_modified(file_path: str, database: DatabaseClient, steamworks_api: SteamworksApi):
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
        match: Match = parse_match(root=parsed_attributes.getroot(), steam_name=steamworks_api.get_persona_name())
    except SteamworksError as exception:
        logging.debug(f"Failed to get the user's display name: {exception=}")
        return
    except ParserError as exception:
        logging.debug(f"Failed to parse the attributes file: {exception=}")
        return

    # Save match data to disk
    if match.try_save_to_file(database=database):
        return  # Skip printing an already existing entry

    # Print useful data from the match
    log_player_data(match)


def log_player_data(match: Match):
    """
    Logs the players on the local team, and all enemies that
      were killed by or killed the local player.
    :param match: a parsed Match instance
    """
    teammates: Generator = (player for team in match.teams for player in team.players if team.own_team)
    enemies: Generator = (player for team in match.teams for player in team.players if not team.own_team)

    # Log the teammates
    logging.info("Teammates:")
    player: Player
    for player in teammates:
        local_player_marker: str = " (you)" if player.name == match.player_name else ""
        logging.info(f"  {Fore.GREEN}{player.name}{Style.RESET_ALL} ({format_mmr(player.mmr)}){local_player_marker}")

    # Log the enemies
    logging.info("Enemies:")
    for player in enemies:
        if player.killed_by_me:
            kill_count: str = f" {player.killed_by_me}x" if player.killed_by_me > 1 else ""
            logging.info(f"  Killed {Fore.GREEN}{player.name}{Style.RESET_ALL} ({format_mmr(player.mmr)}){kill_count}")
        if player.killed_me:
            death_count: str = f" {player.killed_me}x" if player.killed_me > 1 else ""
            logging.info(f"  Died to {Fore.RED}{player.name}{Style.RESET_ALL} ({format_mmr(player.mmr)}){death_count}")


if __name__ == "__main__":
    main()
