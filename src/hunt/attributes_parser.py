import logging
import xml.etree.ElementTree as ElementTree

from .types.team import Team
from .types.player import Player
from .types.match import Match
from .types.match import Entry
from .exceptions import ParserError


def fetch_xpath_value(element: ElementTree.Element, name: str, suffix: str = "") -> str:
    """
    Fetches an element's value based from it's name (and suffix).
    :param element: an XML element
    :param name: the element's name
    :param suffix: a suffix to append to the element
    :return: the value of an element
    :raises AttributeError: if the xpath isn't found or the attribute "value" doesn't exist
    """
    return element.find(path=f"Attr[@name='{name}{'_' + suffix if suffix else ''}']").attrib["value"]


def parse_match(root: ElementTree.Element, steam_name: str) -> Match:
    """
    Parse the element tree for match data.
    :param steam_name: the user's display name
    :param root: the root element tree
    :return: a Match object
    :raises ParserError: if an expected value is not found (AttributeError, parse_teams)
    """
    entries: list[Entry] = []

    try:
        # Determine the expected number of entries to iterate over
        entries_count: int = int(root.find(path="Attr[@name='MissionBagNumEntries']").attrib["value"])
        for entry_id in range(entries_count):
            # Parse each entry
            entry_prefix: str = f"MissionBagEntry_{entry_id}"
            amount: int = int(fetch_xpath_value(root, entry_prefix, "amount"))
            category: str = fetch_xpath_value(root, entry_prefix, "category")
            descriptor_name: str = fetch_xpath_value(root, entry_prefix, "descriptorName")
            descriptor_score: str = fetch_xpath_value(root, entry_prefix, "descriptorScore")
            descriptor_type: str = fetch_xpath_value(root, entry_prefix, "descriptorType")
            reward_type: int = int(fetch_xpath_value(root, entry_prefix, "reward"))
            reward_size: int = int(fetch_xpath_value(root, entry_prefix, "rewardSize"))

            # Append a new Entry object to the list of entries
            entries.append(Entry(amount, category,
                                 descriptor_name, descriptor_score, descriptor_type,
                                 reward_type, reward_size))

        hunter_survived: bool = fetch_xpath_value(root, "MissionBagIsHunterDead") == "false"
        is_quickplay: bool = fetch_xpath_value(root, "MissionBagIsQuickPlay") == "true"
        return Match(steam_name, hunter_survived, is_quickplay, tuple(entries), parse_teams(root=root))
    except AttributeError as exception:
        logging.debug(f"AttributeError when parsing match data: {exception=}")
        raise ParserError("Failed to parse match data.")
    except ParserError as exception:
        logging.debug(f"ParserError when parsing match data: {exception=}")
        raise


def parse_teams(root: ElementTree.Element) -> tuple[Team]:
    """
    Parse the element tree for the available teams.
    :param root: the root element tree
    :return: a tuple of Team objects
    :raises ParserError: if an expected value is not found (AttributeError)
    """
    teams: list[Team] = []

    try:
        # Determine the expected team count and iterate over the teams
        expected_team_count: int = int(fetch_xpath_value(root, "MissionBagNumTeams"))
        for team_id in range(expected_team_count):
            # Parse each team
            team_prefix: str = f"MissionBagTeam_{team_id}"
            randoms: bool = fetch_xpath_value(root, team_prefix, "isinvite") == "false"
            team_mmr: int = int(fetch_xpath_value(root, team_prefix, "mmr"))
            number_of_players: int = int(fetch_xpath_value(root, team_prefix, "numplayers"))
            own_team: bool = fetch_xpath_value(root, team_prefix, "ownteam") == "true"

            players: list[Player] = []
            # Parse each player from the team
            for player_id in range(number_of_players):
                player_prefix: str = f"MissionBagPlayer_{team_id}_{player_id}"
                name: str = fetch_xpath_value(root, player_prefix, "blood_line_name")
                had_wellspring: bool = fetch_xpath_value(root, player_prefix, "hadWellspring") == "true"
                had_bounty: bool = fetch_xpath_value(root, player_prefix, "hadbounty") == "true"
                killed_by_me: int = int(fetch_xpath_value(root, player_prefix, "killedbyme"))
                killed_me: int = int(fetch_xpath_value(root, player_prefix, "killedme"))
                player_mmr: int = int(fetch_xpath_value(root, player_prefix, "mmr"))
                profile_id: int = int(fetch_xpath_value(root, player_prefix, "profileid"))
                used_proximity_chat: bool = fetch_xpath_value(root, player_prefix, "proximity") == "true"
                is_skillbased: bool = fetch_xpath_value(root, player_prefix, "skillbased") == "true"

                # Append a new Player object to the list of players
                players.append(Player(name, had_wellspring, had_bounty, killed_by_me, killed_me,
                                      player_mmr, profile_id, used_proximity_chat, is_skillbased))

            teams.append(Team(randoms, team_mmr, own_team, tuple(players)))
        return tuple(teams)
    except AttributeError as exception:
        logging.debug(f"AttributeError when parsing team data: {exception=}")
        raise ParserError("Failed to parse team data.")
