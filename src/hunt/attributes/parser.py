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
        accolades.append(Accolade.deserialize(root, accolade_id=i))

    # Parse and store the entries
    for i in range(entries_count):
        entries.append(Entry.deserialize(root, entry_id=i))

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
        handicap: int = get_element_value(root, f"{team_prefix}_handicap", result_type=int)
        is_invite: bool = get_element_value(root, f"{team_prefix}_isinvite", result_type=bool)
        team_mmr: int = get_element_value(root, f"{team_prefix}_mmr", result_type=int)
        number_of_players: int = get_element_value(root, f"{team_prefix}_numplayers", result_type=int)
        own_team: bool = get_element_value(root, f"{team_prefix}_ownteam", result_type=bool)

        players: list[Player] = []
        # Parse each player from the team
        for player_id in range(number_of_players):
            players.append(Player.deserialize(root, team_id=team_id, player_id=player_id))

        teams.append(Team(handicap, is_invite, team_mmr, own_team, tuple(players)))
    return tuple(teams)
