import sys
import time
import os.path
import logging
from typing import Generator
from functools import partial

from colorama import Fore, Style, colorama_text

from hunt.constants import RESOURCES_PATH, MATCH_LOGS_PATH, STEAMWORKS_BINARIES_PATH, \
    HUNT_SHOWDOWN_APP_ID, HUNT_SHOWDOWN_TEST_SERVER_APP_ID, \
    DATABASE_PATH, DATABASE_TEST_SERVER_PATH, STEAMWORKS_SDK_PATH
from hunt.database.client import Client as DatabaseClient
from hunt.filesystem.watchdog import FileWatchdog
from hunt.steam.api import SteamworksApi, fetch_hunt_attributes_path, try_extract_steamworks_binaries
from hunt.attributes.parser import ElementTree, Match, Player, parse_match
from hunt.exceptions import SteamworksError, UnsupportedPlatformError, ParserError
from hunt.cli.arguments.parser import Config, parse_arguments
from hunt.cli.exit_codes import ExitCode


def setup_logger(config: Config) -> None:
    """
    Sets up the application logger.
    :param config: the configuration provided by the user
    """
    # Setup logging
    logging.basicConfig(format="[%(asctime)s, %(levelname)s] %(message)s",
                        datefmt="%H:%M", level=logging.INFO if not config.debug else logging.DEBUG,
                        stream=sys.stdout)

    def setup_level_color(level: int, color: str, padding: int = 8) -> None:
        """
        Adjusts a logging level name to add fancy color support.
        :param level: the logger level
        :param color: the color to use
        :param padding: the number of padded whitespace characters
        """
        logging.addLevelName(level, f"{color}{logging.getLevelName(level):>{padding}}{Style.RESET_ALL}")

    # Color config
    color_config: tuple[tuple[int, str], ...] = (
        (logging.DEBUG, Fore.CYAN),
        (logging.INFO, Fore.GREEN),
        (logging.WARNING, Fore.YELLOW),
        (logging.ERROR, Fore.RED),
        (logging.CRITICAL, Style.BRIGHT + Fore.RED))

    # Setup the color levels
    logger_level: int
    level_color: str
    for logger_level, level_color in color_config:
        setup_level_color(logger_level, level_color)


def console_main() -> ExitCode:
    """
    The CLI entry point for the package.
    :return: an exit code.
    """
    # Initialize Colorama
    with colorama_text():
        # Parse the arguments and forward the app config to main
        config: Config = parse_arguments()

        # Setup the logger
        setup_logger(config)

        # Start the application.
        return main(config)


def main(config: Config) -> ExitCode:
    """
    Run the program and provide an exit code.
    :param config: the configuration provided by the user
    :return: an exit code.
    """
    try:
        os.makedirs(name=RESOURCES_PATH, exist_ok=True)  # Create the resource directory if it doesn't exist
        os.makedirs(name=MATCH_LOGS_PATH, exist_ok=True)  # Create the match logs directory if it doesn't exist
        os.makedirs(name=STEAMWORKS_BINARIES_PATH, exist_ok=True)  # Create the bin directory if it doesn't exist
    except OSError as exception:
        logging.critical("Failed to create create application-critical directories in the current working directory. "
                         "Are write permissions missing?")
        logging.debug(f"OS error: {exception=}")
        return ExitCode.FILESYSTEM_ERROR

    try:
        # Extract the Steamworks binaries to disk
        steamworks_api_path: str = try_extract_steamworks_binaries()
    except SteamworksError as exception:
        logging.critical("Failed to extract the Steamworks binaries, are you missing the Steamworks SDK?")
        logging.info(f"The Steamworks SDK should be located at: {STEAMWORKS_SDK_PATH!r}")
        logging.debug(f"Steamworks error: {exception=}")
        return ExitCode.STEAMWORKS_ERROR
    except UnsupportedPlatformError as exception:
        logging.critical("The current platform isn't supported.")
        logging.debug(f"Unsupported platform error: {exception=}")
        return ExitCode.UNSUPPORTED_PLATFORM

    try:
        # Initialize the Steamworks API
        app_id: int = HUNT_SHOWDOWN_APP_ID if not config.test_server else HUNT_SHOWDOWN_TEST_SERVER_APP_ID
        steamworks_api: SteamworksApi = SteamworksApi.prepare_and_initialize(steamworks_api_path, app_id=app_id)
    except SteamworksError as exception:
        logging.critical("A Steamworks API error occurred, is Steam running?")
        logging.debug(f"Steamworks error: {exception=}")
        return ExitCode.STEAMWORKS_ERROR
    else:
        logging.info("Steamworks API initialized.")

    # Locate the attributes file
    attributes_path: str = fetch_hunt_attributes_path(steamworks_api, app_id=app_id)
    assert os.path.exists(attributes_path), "Attributes file does not exist."

    database: DatabaseClient
    database_path: str = DATABASE_PATH if not config.test_server else DATABASE_TEST_SERVER_PATH
    with DatabaseClient(file_path=database_path) as database:
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
    return ExitCode.SUCCESS


def attributes_file_modified(file_path: str, database: DatabaseClient, steamworks_api: SteamworksApi) -> None:
    """
    Invoked when the attributes file is modified;
      Parses the match data from the attributes file and
      saves it to disk.
    :param file_path: the path of the file to parse
    :param database: a DatabaseClient instance
    :param steamworks_api: a SteamworksApi instance
    """
    # Read the file contents
    with open(file_path, "rb") as file:
        file_contents: bytes = file.read()

    # If the file contents are empty, skip parsing
    if not file_contents:
        return

    try:
        # Attempt to parse the attributes file
        parsed_attributes: ElementTree.Element = ElementTree.fromstring(file_contents)
    except ElementTree.ParseError as exception:
        # Skip the update
        logging.error("Failed to parse the attributes file.")
        logging.debug(f"Failed to parse the attributes file: {exception=}")
        return

    # Parse the teams from the attributes file
    try:
        match: Match = parse_match(root=parsed_attributes, steam_name=steamworks_api.get_persona_name())
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
    log_match_data(match)


def log_match_data(match: Match) -> None:
    """
    Logs interesting data about the match such as:
      - rewards collected from the match,
      - players in the team, and
      - enemy players that the player interacted with.
    :param match: a parsed Match instance
    """
    # Log interesting rewards
    def _log_rewards() -> None:
        logging.info("Rewards:")

        # Hunt dollars
        total_hunt_dollars: int = match.rewards.bounty + match.rewards.hunt_dollars
        if total_hunt_dollars:
            logging.info(f"  Received {total_hunt_dollars} hunt dollar(s).")

        # Bloodbonds
        if match.rewards.bloodbonds:
            logging.info(f"  Received {match.rewards.bloodbonds} bloodbond(s).")

        # Hunter-related rewards
        total_xp: int = match.rewards.xp + match.rewards.hunter_xp + match.rewards.bounty * 4
        if total_xp:
            logging.info(f"  Received {total_xp} hunter XP.")
        if match.rewards.hunter_levels:
            logging.info(f"  Received {match.rewards.hunter_levels} perk points.")
        if match.rewards.upgrade_points:
            logging.info(f"  Collected {match.rewards.upgrade_points} upgrade points.")

        # Bloodline XP
        if match.rewards.bloodline_xp:
            logging.info(f"  Collected {match.rewards.bloodline_xp} bloodline XP.")
    # Skip logging if there were no rewards
    if match.rewards:
        _log_rewards()

    # Log players
    def _log_players() -> None:
        teammates: Generator[Player, None, None] = (
            player for team in match.teams for player in team.players if team.own_team)
        enemies: tuple[Player, ...] = tuple(player for team in match.teams
                                            for player in team.players if not team.own_team)

        # Log information about the local team
        logging.info("Team:")
        player: Player
        for player in teammates:
            logging.info(f"  {player.format_name(is_local_player=player.name == match.player_name)}")

        # Log information about the players the local player interacted with
        if any(player.killed_by_me or player.killed_me for player in enemies):
            logging.info("Enemies:")
            for player in enemies:
                if player.killed_by_me:
                    logging.info(f"  {player.format_kills()}")
                if player.killed_me:
                    logging.info(f"  {player.format_deaths()}")
    _log_players()


if __name__ == "__main__":
    raise SystemExit(console_main())
