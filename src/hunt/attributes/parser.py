import xml.etree.ElementTree as ElementTree

from .match import Match, Accolade, Entry, Rewards, Team, Player
from ..exceptions import ParserError
from ..reward_constants import BOUNTY_CATEGORIES, XP_CATEGORIES, HUNT_DOLLARS_CATEGORY, BLOODBONDS_CATEGORY, \
    HUNTER_XP_DESCRIPTOR_NAME, HUNTER_XP_REWARD_TYPE, HUNTER_LEVELS_CATEGORY, \
    UPGRADE_POINTS_DESCRIPTOR_NAME, BLOODLINE_DESCRIPTOR_NAME


def _fetch_xpath_value(element: ElementTree.Element, name: str, suffix: str = "") -> str:
    """
    Fetches an element's value based from it's name (and suffix).
    :param element: an XML element
    :param name: the element's name
    :param suffix: a suffix to append to the element
    :return: the value of an element
    :raises ParserError: if the xpath isn't found
    """
    path: str = f"Attr[@name='{name}{'_' + suffix if suffix else ''}']"
    resolved_element: ElementTree.Element | None = element.find(path=path)
    if resolved_element is not None:
        return resolved_element.attrib["value"]
    raise ParserError(f"No such element {path!r} in the XML element tree.")


def _calculate_rewards(accolades: tuple[Accolade, ...], entries: tuple[Entry, ...],
                       hunt_dollar_bonus: int, hunter_xp_bonus: int) -> Rewards:
    """
    Calculates all the rewards collected from a match.
    :param accolades: a tuple of Accolade instances
    :param entries: a tuple of Entry instances
    :return: a Rewards instance
    """
    generated_bloodbonds: int = sum(accolade.generated_bloodbonds for accolade in accolades)
    bounty: int = sum(entry.reward_size for entry in entries if entry.category in BOUNTY_CATEGORIES)
    xp: int = sum(entry.reward_size for entry in entries if entry.category in XP_CATEGORIES)
    hunt_dollars: int = sum(entry.reward_size for entry in entries if entry.category == HUNT_DOLLARS_CATEGORY)
    bloodbonds: int = sum(entry.reward_size for entry in entries if entry.category == BLOODBONDS_CATEGORY)
    hunter_xp: int = sum(entry.reward_size for entry in entries
                         if entry.descriptor_name == HUNTER_XP_DESCRIPTOR_NAME
                         and entry.reward_type == HUNTER_XP_REWARD_TYPE)
    hunter_levels: int = sum(entry.reward_size for entry in entries if entry.category == HUNTER_LEVELS_CATEGORY)
    upgrade_points: int = sum(entry.reward_size for entry in entries
                              if entry.descriptor_name == UPGRADE_POINTS_DESCRIPTOR_NAME)
    bloodline_xp: int = sum(entry.reward_size for entry in entries
                            if entry.descriptor_name == BLOODLINE_DESCRIPTOR_NAME)

    return Rewards(bounty, xp + hunter_xp_bonus, hunt_dollars + hunt_dollar_bonus, generated_bloodbonds + bloodbonds,
                   hunter_xp, hunter_levels, upgrade_points, bloodline_xp)


def _parse_missionaccoladeentry(root: ElementTree.Element, element_id: int) -> Accolade:
    """
    Parses a MissionAccoladeEntry element.
    :param root: an XML element
    :param element_id: the id of the entry element
    :return: an Accolade instance
    :raises ParserError: if the xpath isn't found (_fetch_xpath_value)
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
    :raises ParserError: if the xpath isn't found (_fetch_xpath_value)
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


def _parse_player(root: ElementTree.Element, team_id: int, player_id: int) -> Player:
    """
    Parses a MissionBagPlayer element.
    :param root: an XML element
    :param team_id: the id of the player's team
    :param player_id: the id of the player in the team
    :return: a Player instance
    :raises ParserError: if the xpath isn't found (_fetch_xpath_value)
    """
    # Define the prefix
    element_prefix: str = f"MissionBagPlayer_{team_id}_{player_id}"

    # Parse each entry
    name: str = _fetch_xpath_value(root, element_prefix, "blood_line_name")
    bounties_extracted: int = int(_fetch_xpath_value(root, element_prefix, "bountyextracted"))
    bounties_picked_up: int = int(_fetch_xpath_value(root, element_prefix, "bountypickedup"))
    downed_by_me: int = int(_fetch_xpath_value(root, element_prefix, "downedbyme"))
    downed_by_teammate: int = int(_fetch_xpath_value(root, element_prefix, "downedbyteammate"))
    downed_me: int = int(_fetch_xpath_value(root, element_prefix, "downedme"))
    downed_teammate: int = int(_fetch_xpath_value(root, element_prefix, "downedteammate"))
    had_wellspring: bool = _fetch_xpath_value(root, element_prefix, "hadWellspring") == "true"
    is_partner: bool = _fetch_xpath_value(root, element_prefix, "ispartner") == "true"
    is_soul_survivor: bool = _fetch_xpath_value(root, element_prefix, "issoulsurvivor") == "true"
    killed_by_me: int = int(_fetch_xpath_value(root, element_prefix, "killedbyme"))
    killed_by_teammate: int = int(_fetch_xpath_value(root, element_prefix, "killedbyteammate"))
    killed_me: int = int(_fetch_xpath_value(root, element_prefix, "killedme"))
    killed_teammate: int = int(_fetch_xpath_value(root, element_prefix, "killedteammate"))
    mmr: int = int(_fetch_xpath_value(root, element_prefix, "mmr"))
    profile_id: int = int(_fetch_xpath_value(root, element_prefix, "profileid"))
    proximity_to_me: bool = _fetch_xpath_value(root, element_prefix, "proximitytome") == "true"
    proximity_to_teammate: bool = _fetch_xpath_value(root, element_prefix, "proximitytoteammate") == "true"
    skillbased: bool = _fetch_xpath_value(root, element_prefix, "skillbased") == "true"
    teamextraction: bool = _fetch_xpath_value(root, element_prefix, "teamextraction") == "true"

    # Return the player
    return Player(name, bounties_extracted, bounties_picked_up, downed_by_me, downed_by_teammate,
                  downed_me, downed_teammate, had_wellspring, is_partner, is_soul_survivor,
                  killed_by_me, killed_by_teammate, killed_me, killed_teammate, mmr, profile_id,
                  proximity_to_me, proximity_to_teammate, skillbased, teamextraction)


def parse_match(root: ElementTree.Element, steam_name: str) -> Match:
    """
    Parse the element tree for match data.
    :param root: the root element tree
    :param steam_name: the user's display name
    :return: a Match object
    :raises ParserError: if the xpath isn't found (ParserError;
                         _parse_missionaccoladeentry, _parse_missionbagentry, parse_teams)
    """
    accolades: list[Accolade] = []
    entries: list[Entry] = []

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

    accolades_tuple: tuple[Accolade, ...] = tuple(accolades)
    entries_tuple: tuple[Entry, ...] = tuple(entries)
    return Match(steam_name, hunter_survived, is_quickplay, accolades_tuple, entries_tuple,
                 _calculate_rewards(accolades_tuple, entries_tuple, hunt_dollar_bonus, hunter_xp_bonus),
                 parse_teams(root=root))


def parse_teams(root: ElementTree.Element) -> tuple[Team, ...]:
    """
    Parse the element tree for the available teams.
    :param root: the root element tree
    :return: a tuple of Team objects
    :raises ParserError: if the xpath isn't found (_fetch_xpath_value)
    """
    teams: list[Team] = []

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
            players.append(_parse_player(root, team_id=team_id, player_id=player_id))

        teams.append(Team(handicap, is_invite, team_mmr, own_team, tuple(players)))
    return tuple(teams)
