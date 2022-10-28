from .match import Accolade, Entry, Match, Player, Rewards, Team
from .team import SerializableTeam
from .xml.elements import XmlElement, get_element_value
from ..reward_constants import BLOODBONDS_CATEGORY, BLOODLINE_DESCRIPTOR_NAME, BOUNTY_CATEGORIES, \
    HUNTER_LEVELS_CATEGORY, HUNTER_XP_DESCRIPTOR_NAME, HUNTER_XP_REWARD_TYPE, HUNT_DOLLARS_CATEGORY, \
    UPGRADE_POINTS_DESCRIPTOR_NAME, XP_CATEGORIES


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
    event_points: int = sum(accolade.event_points for accolade in accolades)

    return Rewards(bounty, xp + hunter_xp_bonus, hunt_dollars + hunt_dollar_bonus, generated_bloodbonds + bloodbonds,
                   hunter_xp, hunter_levels, upgrade_points, bloodline_xp, event_points)


def parse_match(root: XmlElement, steam_name: str) -> Match:
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

    bloodline_rank: int = get_element_value(root, "Unlocks/UnlockRank", result_type=int)
    hunt_dollar_bonus: int = get_element_value(root, "MissionBagFbeGoldBonus", result_type=int)
    hunter_xp_bonus: int = get_element_value(root, "MissionBagFbeHunterXpBonus", result_type=int)
    is_hunter_dead: bool = get_element_value(root, "MissionBagIsHunterDead", result_type=bool)
    is_quickplay: bool = get_element_value(root, "MissionBagIsQuickPlay", result_type=bool)
    region: str = get_element_value(root, "Region")
    secondary_region: str = get_element_value(root, "SecondaryRegion")

    accolades_tuple: tuple[Accolade, ...] = tuple(accolades)
    entries_tuple: tuple[Entry, ...] = tuple(entries)
    return Match(steam_name, bloodline_rank, is_hunter_dead, is_quickplay, region, secondary_region,
                 accolades_tuple, entries_tuple,
                 _calculate_rewards(accolades_tuple, entries_tuple, hunt_dollar_bonus, hunter_xp_bonus),
                 parse_teams(root=root))


def parse_teams(root: XmlElement) -> tuple[Team, ...]:
    """
    Parse the element tree for the available teams.
    :param root: the root element tree
    :return: a tuple of Team objects
    :raises ParserError: from get_element_value
    """
    teams: list[Team] = []

    # Determine the expected team count and iterate over the teams
    expected_team_count: int = get_element_value(root, "MissionBagNumTeams", result_type=int)
    for i in range(expected_team_count):
        # Parse each team
        parsed_team: SerializableTeam = SerializableTeam.deserialize(root, team_id=i)

        players: list[Player] = []
        # Parse each player from the team
        for j in range(parsed_team.players_count):
            players.append(Player.deserialize(root, team_id=i, player_id=j))

        teams.append(Team(parsed_team.handicap, parsed_team.is_invite, parsed_team.mmr, parsed_team.own_team,
                          tuple(players)))
    return tuple(teams)
