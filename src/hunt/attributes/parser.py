import logging
import xml.etree.ElementTree as ElementTree

from .match import Match, Accolade, Entry, Rewards, Team, Player
from ..exceptions import ParserError
from ..reward_constants import BOUNTY_CATEGORIES, XP_CATEGORIES, HUNT_DOLLARS_CATEGORY, BLOODBONDS_CATEGORY, \
    HUNTER_XP_CATEGORY, HUNTER_XP_REWARD_TYPE, HUNTER_LEVELS_CATEGORY, \
    UPGRADE_POINTS_DESCRIPTOR_NAME, BLOODLINE_DESCRIPTOR_NAME


def _fetch_xpath_value(element: ElementTree.Element, name: str, suffix: str = "") -> str:
    """
    Fetches an element's value based from it's name (and suffix).
    :param element: an XML element
    :param name: the element's name
    :param suffix: a suffix to append to the element
    :return: the value of an element
    :raises AttributeError: if the xpath isn't found or the attribute "value" doesn't exist
    """
    return element.find(path=f"Attr[@name='{name}{'_' + suffix if suffix else ''}']").attrib["value"]


def _calculate_rewards(entries: tuple[Entry, ...], hunt_dollar_bonus: int, hunter_xp_bonus: int) -> Rewards:
    """
    Calculates all the rewards collected from a match.
    :param entries: a tuple of Entry instances
    :return: a Rewards instance
    """
    bounty: int = sum(entry.reward_size for entry in entries if entry.category in BOUNTY_CATEGORIES)
    xp: int = sum(entry.reward_size for entry in entries if entry.category in XP_CATEGORIES)
    hunt_dollars: int = sum(entry.reward_size for entry in entries if entry.category == HUNT_DOLLARS_CATEGORY)
    bloodbonds: int = sum(entry.reward_size for entry in entries if entry.category == BLOODBONDS_CATEGORY)
    hunter_xp: int = sum(entry.reward_size for entry in entries
                         if entry.category == HUNTER_XP_CATEGORY and entry.reward_type == HUNTER_XP_REWARD_TYPE)
    hunter_levels: int = sum(entry.reward_size for entry in entries if entry.category == HUNTER_LEVELS_CATEGORY)
    upgrade_points: int = sum(entry.reward_size for entry in entries
                              if entry.descriptor_name == UPGRADE_POINTS_DESCRIPTOR_NAME)
    bloodline_xp: int = sum(entry.reward_size for entry in entries
                            if entry.descriptor_name == BLOODLINE_DESCRIPTOR_NAME)

    return Rewards(bounty, xp + hunter_xp_bonus, hunt_dollars + hunt_dollar_bonus, bloodbonds,
                   hunter_xp, hunter_levels, upgrade_points, bloodline_xp)


def _parse_missionaccoladeentry(root: ElementTree.Element, element_id: int) -> Accolade:
    """
    Parses a MissionAccoladeEntry element.
    :param root: an XML element
    :param element_id: the id of the entry element
    :return: an Accolade instance
    :raises AttributeError: if the xpath isn't found or the attribute "value" doesn't exist (_fetch_xpath_value)
    """
    # Define the prefix
    element_prefix: str = f"MissionAccoladeEntry_{element_id}"

    # Parse each entry
    bloodline_xp: int = int(_fetch_xpath_value(root, element_prefix, "bloodlineXp"))
    bounty: int = int(_fetch_xpath_value(root, element_prefix, "bounty"))
    category: str = _fetch_xpath_value(root, element_prefix, "category")
    event_points: int = int(_fetch_xpath_value(root, element_prefix, "eventPoints"))
    bloodbonds: int = int(_fetch_xpath_value(root, element_prefix, "gems"))
    generated_bloodbonds: int = int(_fetch_xpath_value(root, element_prefix, "generatedGems"))
    hunt_dollars: int = int(_fetch_xpath_value(root, element_prefix, "gold"))
    hits: int = int(_fetch_xpath_value(root, element_prefix, "hits"))
    hunter_points: int = int(_fetch_xpath_value(root, element_prefix, "hunterPoints"))
    hunter_xp: int = int(_fetch_xpath_value(root, element_prefix, "hunterXp"))
    weighting: int = int(_fetch_xpath_value(root, element_prefix, "weighting"))
    xp: int = int(_fetch_xpath_value(root, element_prefix, "xp"))

    return Accolade(bloodline_xp, bounty, category, event_points, bloodbonds, generated_bloodbonds,
                    hunt_dollars, hits, hunter_points, hunter_xp, weighting, xp)


def _parse_missionbagentry(root: ElementTree.Element, element_id: int) -> Entry:
    """
    Parses a MissionBagEntry element.
    :param root: an XML element
    :param element_id: the id of the entry element
    :return: an Entry instance
    :raises AttributeError: if the xpath isn't found or the attribute "value" doesn't exist (_fetch_xpath_value)
    """
    # Define the prefix
    element_prefix: str = f"MissionBagEntry_{element_id}"

    # Parse each entry
    amount: int = int(_fetch_xpath_value(root, element_prefix, "amount"))
    category: str = _fetch_xpath_value(root, element_prefix, "category")
    descriptor_name: str = _fetch_xpath_value(root, element_prefix, "descriptorName")
    descriptor_score: int = int(_fetch_xpath_value(root, element_prefix, "descriptorScore"))
    descriptor_type: int = int(_fetch_xpath_value(root, element_prefix, "descriptorType"))
    reward_type: int = int(_fetch_xpath_value(root, element_prefix, "reward"))
    reward_size: int = int(_fetch_xpath_value(root, element_prefix, "rewardSize"))

    # Return the entry
    return Entry(amount, category, descriptor_name, descriptor_score, descriptor_type, reward_type, reward_size)


def parse_match(root: ElementTree.Element, steam_name: str) -> Match:
    """
    Parse the element tree for match data.
    :param steam_name: the user's display name
    :param root: the root element tree
    :return: a Match object
    :raises ParserError: if an expected value is not found (AttributeError, parse_teams)
    """
    accolades: list[Accolade] = []
    entries: list[Entry] = []

    try:
        # Determine the expected number of accolades and entries to iterate
        accolades_count: int = int(_fetch_xpath_value(root, "MissionBagNumAccolades"))
        entries_count: int = int(_fetch_xpath_value(root, "MissionBagNumEntries"))

        # Parse and store the accolades
        for i in range(accolades_count):
            accolades.append(_parse_missionaccoladeentry(root, element_id=i))

        # Parse and store the entries
        for i in range(entries_count):
            entries.append(_parse_missionbagentry(root, element_id=i))

        hunt_dollar_bonus: int = int(_fetch_xpath_value(root, "MissionBagFbeGoldBonus"))
        hunter_xp_bonus: int = int(_fetch_xpath_value(root, "MissionBagFbeHunterXpBonus"))
        hunter_survived: bool = _fetch_xpath_value(root, "MissionBagIsHunterDead") == "false"
        is_quickplay: bool = _fetch_xpath_value(root, "MissionBagIsQuickPlay") == "true"
        return Match(steam_name, hunter_survived, is_quickplay,
                     tuple(accolades), tuple(entries),
                     _calculate_rewards(tuple(entries), hunt_dollar_bonus, hunter_xp_bonus),
                     parse_teams(root=root))
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
        expected_team_count: int = int(_fetch_xpath_value(root, "MissionBagNumTeams"))
        for team_id in range(expected_team_count):
            # Parse each team
            team_prefix: str = f"MissionBagTeam_{team_id}"
            handicap: int = int(_fetch_xpath_value(root, team_prefix, "handicap"))
            is_invite: bool = _fetch_xpath_value(root, team_prefix, "isinvite") == "true"
            team_mmr: int = int(_fetch_xpath_value(root, team_prefix, "mmr"))
            number_of_players: int = int(_fetch_xpath_value(root, team_prefix, "numplayers"))
            own_team: bool = _fetch_xpath_value(root, team_prefix, "ownteam") == "true"

            players: list[Player] = []
            # Parse each player from the team
            for player_id in range(number_of_players):
                player_prefix: str = f"MissionBagPlayer_{team_id}_{player_id}"
                name: str = _fetch_xpath_value(root, player_prefix, "blood_line_name")
                had_wellspring: bool = _fetch_xpath_value(root, player_prefix, "hadWellspring") == "true"
                had_bounty: bool = _fetch_xpath_value(root, player_prefix, "hadbounty") == "true"
                killed_by_me: int = int(_fetch_xpath_value(root, player_prefix, "killedbyme"))
                killed_me: int = int(_fetch_xpath_value(root, player_prefix, "killedme"))
                player_mmr: int = int(_fetch_xpath_value(root, player_prefix, "mmr"))
                profile_id: int = int(_fetch_xpath_value(root, player_prefix, "profileid"))
                used_proximity_chat: bool = _fetch_xpath_value(root, player_prefix, "proximity") == "true"
                is_skillbased: bool = _fetch_xpath_value(root, player_prefix, "skillbased") == "true"

                # Append a new Player object to the list of players
                players.append(Player(name, had_wellspring, had_bounty, killed_by_me, killed_me,
                                      player_mmr, profile_id, used_proximity_chat, is_skillbased))

            teams.append(Team(handicap, is_invite, team_mmr, own_team, tuple(players)))
        return tuple(teams)
    except AttributeError as exception:
        logging.debug(f"AttributeError when parsing team data: {exception=}")
        raise ParserError("Failed to parse team data.")
