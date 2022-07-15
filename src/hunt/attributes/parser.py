import xml.etree.ElementTree as ElementTree

from .xml.elements import get_element_value
from .match import Match, Accolade, Entry, Rewards, Team, Player
from ..reward_constants import BOUNTY_CATEGORIES, XP_CATEGORIES, HUNT_DOLLARS_CATEGORY, BLOODBONDS_CATEGORY, \
    HUNTER_XP_DESCRIPTOR_NAME, HUNTER_XP_REWARD_TYPE, HUNTER_LEVELS_CATEGORY, \
    UPGRADE_POINTS_DESCRIPTOR_NAME, BLOODLINE_DESCRIPTOR_NAME


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
    :raises ParserError: from get_element_value
    """
    # Define the prefix
    element_prefix: str = f"MissionAccoladeEntry_{element_id}"

    # Parse each entry
    bloodline_xp: int = get_element_value(root, element_prefix, "bloodlineXp", result_type=int)
    bounty: int = get_element_value(root, element_prefix, "bounty", result_type=int)
    category: str = get_element_value(root, element_prefix, "category")
    event_points: int = get_element_value(root, element_prefix, "eventPoints", result_type=int)
    bloodbonds: int = get_element_value(root, element_prefix, "gems", result_type=int)
    generated_bloodbonds: int = get_element_value(root, element_prefix, "generatedGems", result_type=int)
    hunt_dollars: int = get_element_value(root, element_prefix, "gold", result_type=int)
    hits: int = get_element_value(root, element_prefix, "hits", result_type=int)
    hunter_points: int = get_element_value(root, element_prefix, "hunterPoints", result_type=int)
    hunter_xp: int = get_element_value(root, element_prefix, "hunterXp", result_type=int)
    weighting: int = get_element_value(root, element_prefix, "weighting", result_type=int)
    xp: int = get_element_value(root, element_prefix, "xp", result_type=int)

    return Accolade(bloodline_xp, bounty, category, event_points, bloodbonds, generated_bloodbonds,
                    hunt_dollars, hits, hunter_points, hunter_xp, weighting, xp)


def _parse_missionbagentry(root: ElementTree.Element, element_id: int) -> Entry:
    """
    Parses a MissionBagEntry element.
    :param root: an XML element
    :param element_id: the id of the entry element
    :return: an Entry instance
    :raises ParserError: from get_element_value
    """
    # Define the prefix
    element_prefix: str = f"MissionBagEntry_{element_id}"

    # Parse each entry
    amount: int = get_element_value(root, element_prefix, "amount", result_type=int)
    category: str = get_element_value(root, element_prefix, "category")
    descriptor_name: str = get_element_value(root, element_prefix, "descriptorName")
    descriptor_score: int = get_element_value(root, element_prefix, "descriptorScore", result_type=int)
    descriptor_type: int = get_element_value(root, element_prefix, "descriptorType", result_type=int)
    reward_type: int = get_element_value(root, element_prefix, "reward", result_type=int)
    reward_size: int = get_element_value(root, element_prefix, "rewardSize", result_type=int)

    # Return the entry
    return Entry(amount, category, descriptor_name, descriptor_score, descriptor_type, reward_type, reward_size)


def _parse_player(root: ElementTree.Element, team_id: int, player_id: int) -> Player:
    """
    Parses a MissionBagPlayer element.
    :param root: an XML element
    :param team_id: the id of the player's team
    :param player_id: the id of the player in the team
    :return: a Player instance
    :raises ParserError: from get_element_value
    """
    # Define the prefix
    element_prefix: str = f"MissionBagPlayer_{team_id}_{player_id}"

    # Parse each entry
    name: str = get_element_value(root, element_prefix, "blood_line_name")
    bounties_extracted: int = get_element_value(root, element_prefix, "bountyextracted", result_type=int)
    bounties_picked_up: int = get_element_value(root, element_prefix, "bountypickedup", result_type=int)
    downed_by_me: int = get_element_value(root, element_prefix, "downedbyme", result_type=int)
    downed_by_teammate: int = get_element_value(root, element_prefix, "downedbyteammate", result_type=int)
    downed_me: int = get_element_value(root, element_prefix, "downedme", result_type=int)
    downed_teammate: int = get_element_value(root, element_prefix, "downedteammate", result_type=int)
    had_wellspring: bool = get_element_value(root, element_prefix, "hadWellspring", result_type=bool)
    is_partner: bool = get_element_value(root, element_prefix, "ispartner", result_type=bool)
    is_soul_survivor: bool = get_element_value(root, element_prefix, "issoulsurvivor", result_type=bool)
    killed_by_me: int = get_element_value(root, element_prefix, "killedbyme", result_type=int)
    killed_by_teammate: int = get_element_value(root, element_prefix, "killedbyteammate", result_type=int)
    killed_me: int = get_element_value(root, element_prefix, "killedme", result_type=int)
    killed_teammate: int = get_element_value(root, element_prefix, "killedteammate", result_type=int)
    mmr: int = get_element_value(root, element_prefix, "mmr", result_type=int)
    profile_id: int = get_element_value(root, element_prefix, "profileid", result_type=int)
    proximity_to_me: bool = get_element_value(root, element_prefix, "proximitytome", result_type=bool)
    proximity_to_teammate: bool = get_element_value(root, element_prefix, "proximitytoteammate", result_type=bool)
    skillbased: bool = get_element_value(root, element_prefix, "skillbased", result_type=bool)
    teamextraction: bool = get_element_value(root, element_prefix, "teamextraction", result_type=bool)

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
    :raises ParserError: from get_element_value
    """
    accolades: list[Accolade] = []
    entries: list[Entry] = []

    # Determine the expected number of accolades and entries to iterate
    accolades_count: int = get_element_value(root, "MissionBagNumAccolades", result_type=int)
    entries_count: int = get_element_value(root, "MissionBagNumEntries", result_type=int)

    # Parse and store the accolades
    for i in range(accolades_count):
        accolades.append(_parse_missionaccoladeentry(root, element_id=i))

    # Parse and store the entries
    for i in range(entries_count):
        entries.append(_parse_missionbagentry(root, element_id=i))

    hunt_dollar_bonus: int = get_element_value(root, "MissionBagFbeGoldBonus", result_type=int)
    hunter_xp_bonus: int = get_element_value(root, "MissionBagFbeHunterXpBonus", result_type=int)
    hunter_is_dead: bool = get_element_value(root, "MissionBagIsHunterDead", result_type=bool)
    is_quickplay: bool = get_element_value(root, "MissionBagIsQuickPlay", result_type=bool)

    accolades_tuple: tuple[Accolade, ...] = tuple(accolades)
    entries_tuple: tuple[Entry, ...] = tuple(entries)
    return Match(steam_name, not hunter_is_dead, is_quickplay, accolades_tuple, entries_tuple,
                 _calculate_rewards(accolades_tuple, entries_tuple, hunt_dollar_bonus, hunter_xp_bonus),
                 parse_teams(root=root))


def parse_teams(root: ElementTree.Element) -> tuple[Team, ...]:
    """
    Parse the element tree for the available teams.
    :param root: the root element tree
    :return: a tuple of Team objects
    :raises ParserError: from get_element_value
    """
    teams: list[Team] = []

    # Determine the expected team count and iterate over the teams
    expected_team_count: int = get_element_value(root, "MissionBagNumTeams", result_type=int)
    for team_id in range(expected_team_count):
        # Parse each team
        team_prefix: str = f"MissionBagTeam_{team_id}"
        handicap: int = get_element_value(root, team_prefix, "handicap", result_type=int)
        is_invite: bool = get_element_value(root, team_prefix, "isinvite", result_type=bool)
        team_mmr: int = get_element_value(root, team_prefix, "mmr", result_type=int)
        number_of_players: int = get_element_value(root, team_prefix, "numplayers", result_type=int)
        own_team: bool = get_element_value(root, team_prefix, "ownteam", result_type=bool)

        players: list[Player] = []
        # Parse each player from the team
        for player_id in range(number_of_players):
            players.append(_parse_player(root, team_id=team_id, player_id=player_id))

        teams.append(Team(handicap, is_invite, team_mmr, own_team, tuple(players)))
    return tuple(teams)
