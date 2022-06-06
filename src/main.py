import time
import json
import os.path
from zlib import crc32
from datetime import datetime

from colorama import Fore, Style

from src.hunt.utilities.hunt import find_hunt_attributes_path
from src.hunt.attributes_parser import ElementTree, Team, Player, parse_teams
from src.hunt.constants import USER_PROFILE_ID, RESOURCES_PATH
from src.hunt.utilities.file_watcher import FileWatchdog

TEAM_HASHES: list[int] = []


def main():
    attributes_path: str = find_hunt_attributes_path()
    assert os.path.exists(attributes_path), "Attributes file does not exist."

    # attributes_file_changed(attributes_path)
    file_watchdog: FileWatchdog = FileWatchdog(file_path=attributes_path, callback=attributes_file_changed)
    file_watchdog.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        file_watchdog.stop()
    file_watchdog.join()


def attributes_file_changed(file_path: str):
    try:
        parsed_attributes: ElementTree = ElementTree.parse(source=file_path)
    except ElementTree.ParseError:
        return
    teams: tuple[Team] = parse_teams(root=parsed_attributes.getroot())

    # Prevent printing the same data multiple times and save them to a file
    team_hash: int = hash(teams)
    if team_hash in TEAM_HASHES:
        return
    TEAM_HASHES.append(team_hash)
    save_teams_to_file(teams)

    players: tuple[Player] = tuple(player for team in teams for player in team.players)
    players_killed: tuple[Player] = tuple(filter(lambda player: player.killed_by_me, players))
    players_killed_me: tuple[Player] = tuple(filter(lambda player: player.killed_me, players))
    user_mmr: int = next(filter(lambda player: player.profile_id == USER_PROFILE_ID, players)).mmr

    print(f"User MMR: {format_mmr(user_mmr)}")
    player: Player
    for player in players_killed_me:
        print(f"  Killed by {Fore.RED}{player.name}{Style.RESET_ALL} ({format_mmr(player.mmr)})")
    for player in players_killed:
        print(f"  Killed {Fore.GREEN}{player.name}{Style.RESET_ALL} ({format_mmr(player.mmr)})")


def save_teams_to_file(teams: tuple[Team]):
    if not teams:
        return

    now: datetime = datetime.now()
    teams_json: str = json.dumps(teams, indent=2, default=vars)

    # Generate the file path
    teams_hash: int = crc32(teams_json.encode())
    generated_file_path: str = os.path.join(RESOURCES_PATH,
                                            f"{now.year}-{now.month:02d}-{now.day:02d}",
                                            f"{now.hour:02d}-{now.minute:02d}-{teams_hash:08x}.json")

    # Create the directories
    directory_path: str = os.path.dirname(generated_file_path)
    os.makedirs(name=directory_path, exist_ok=True)

    # Check if the file already exists
    for file_name in os.listdir(directory_path):
        if f"{teams_hash:08x}" in file_name:
            return

    # Save the file
    with open(generated_file_path, mode="w") as file:
        file.write(teams_json)


def format_mmr(mmr: int) -> str:
    star: str = "★"
    ranges: tuple[int, ...] = (0, 2000, 2300, 2600, 2750, 3000)
    stars: int = len(ranges) - len([x for x in ranges if mmr < x])

    return f"{Fore.BLUE}{mmr}{Style.RESET_ALL} {Fore.LIGHTYELLOW_EX}{star * stars}{Style.RESET_ALL}"


if __name__ == "__main__":
    main()
