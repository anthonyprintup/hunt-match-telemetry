import xml.etree.ElementTree as ElementTree
from .types.team import Team
from .types.player import Player
from .types.match import Match
from .types.match import Entry
from .utilities.steam import fetch_steam_username


def parse_match(root: ElementTree.Element) -> Match:
    """
    Parse the element tree for match data.
    :param root: the root element tree
    :return: a Match object
    :throws: AttributeError if an expected value is not found
    """
    entries: list[Entry] = []

    # Determine the expected number of entries to iterate over
    entries_count: int = int(root.find(path="Attr[@name='MissionBagNumEntries']").attrib["value"])
    for entry_id in range(entries_count):
        # Parse each entry
        entry_prefix: str = f"MissionBagEntry_{entry_id}"
        amount: int = int(root.find(path=f"Attr[@name='{entry_prefix}_amount']").attrib["value"])
        category: str = root.find(path=f"Attr[@name='{entry_prefix}_category']").attrib["value"]
        descriptor_name: str = root.find(path=f"Attr[@name='{entry_prefix}_descriptorName']").attrib["value"]
        descriptor_score: str = root.find(path=f"Attr[@name='{entry_prefix}_descriptorScore']").attrib["value"]
        descriptor_type: str = root.find(path=f"Attr[@name='{entry_prefix}_descriptorType']").attrib["value"]
        reward_type: int = int(root.find(path=f"Attr[@name='{entry_prefix}_reward']").attrib["value"])
        reward_size: int = int(root.find(path=f"Attr[@name='{entry_prefix}_rewardSize']").attrib["value"])

        # Append a new Entry object to the list of entries
        entries.append(Entry(amount, category,
                             descriptor_name, descriptor_score, descriptor_type,
                             reward_type, reward_size))

    hunter_survived: bool = root.find(path="Attr[@name='MissionBagIsHunterDead']").attrib["value"] == "false"
    is_quickplay: bool = root.find(path="Attr[@name='MissionBagIsQuickPlay']").attrib["value"] == "true"
    return Match(fetch_steam_username(), hunter_survived, is_quickplay, tuple(entries), parse_teams(root=root))


def parse_teams(root: ElementTree.Element) -> tuple[Team]:
    """
    Parse the element tree for the available teams.
    :param root: the root element tree
    :return: a tuple of Team objects
    :throws: AttributeError if an expected value is not found
    """
    teams: list[Team] = []

    # Determine the expected team count and iterate over the teams
    expected_team_count: int = int(root.find(path="Attr[@name='MissionBagNumTeams']").attrib["value"])
    for team_id in range(expected_team_count):
        # Parse each team
        team_prefix: str = f"MissionBagTeam_{team_id}"
        randoms: bool = root.find(f"Attr[@name='{team_prefix}_isinvite']").attrib["value"] == "false"
        team_mmr: int = int(root.find(f"Attr[@name='{team_prefix}_mmr']").attrib["value"])
        number_of_players: int = int(root.find(f"Attr[@name='{team_prefix}_numplayers']").attrib["value"])
        own_team: bool = root.find(f"Attr[@name='{team_prefix}_ownteam']").attrib["value"] == "true"

        players: list[Player] = []
        # Parse each player from the team
        for player_id in range(number_of_players):
            player_prefix: str = f"MissionBagPlayer_{team_id}_{player_id}"
            name: str = root.find(f"Attr[@name='{player_prefix}_blood_line_name']").attrib["value"]
            had_wellspring: bool = root.find(f"Attr[@name='{player_prefix}_hadWellspring']").attrib["value"] == "true"
            had_bounty: bool = root.find(f"Attr[@name='{player_prefix}_hadbounty']").attrib["value"] == "true"
            killed_by_me: int = int(root.find(f"Attr[@name='{player_prefix}_killedbyme']").attrib["value"])
            killed_me: int = int(root.find(f"Attr[@name='{player_prefix}_killedme']").attrib["value"])
            player_mmr: int = int(root.find(f"Attr[@name='{player_prefix}_mmr']").attrib["value"])
            profile_id: int = int(root.find(f"Attr[@name='{player_prefix}_profileid']").attrib["value"])
            used_proximity_chat: bool = root.find(f"Attr[@name='{player_prefix}_proximity']").attrib["value"] == "true"
            is_skillbased: bool = root.find(f"Attr[@name='{player_prefix}_skillbased']").attrib["value"] == "true"

            # Append a new Player object to the list of players
            players.append(Player(name, had_wellspring, had_bounty, killed_by_me, killed_me, player_mmr, profile_id,
                                  used_proximity_chat, is_skillbased))

        teams.append(Team(randoms, team_mmr, own_team, tuple(players)))
    return tuple(teams)
