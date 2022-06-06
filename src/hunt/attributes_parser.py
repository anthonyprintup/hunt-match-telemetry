import xml.etree.ElementTree as ElementTree
from .types.team import Team
from .types.player import Player


def parse_teams(root: ElementTree.Element) -> tuple[Team]:
    teams: list[Team] = []

    expected_team_count: int = int(root.find(path="Attr[@name='MissionBagNumTeams']").attrib["value"])
    for team_id in range(expected_team_count):
        team_prefix: str = f"MissionBagTeam_{team_id}"
        randoms: bool = root.find(f"Attr[@name='{team_prefix}_isinvite']").attrib["value"] == "false"
        team_mmr: int = int(root.find(f"Attr[@name='{team_prefix}_mmr']").attrib["value"])
        number_of_players: int = int(root.find(f"Attr[@name='{team_prefix}_numplayers']").attrib["value"])
        own_team: bool = root.find(f"Attr[@name='{team_prefix}_ownteam']").attrib["value"] == "true"

        players: list[Player] = []
        for player_id in range(number_of_players):
            player_prefix: str = f"MissionBagPlayer_{team_id}_{player_id}"
            name: str = root.find(f"Attr[@name='{player_prefix}_blood_line_name']").attrib["value"]
            killed_by_me: bool = root.find(f"Attr[@name='{player_prefix}_killedbyme']").attrib["value"] == "1"
            killed_me: bool = root.find(f"Attr[@name='{player_prefix}_killedme']").attrib["value"] == "1"
            player_mmr: int = int(root.find(f"Attr[@name='{player_prefix}_mmr']").attrib["value"])
            profile_id: int = int(root.find(f"Attr[@name='{player_prefix}_profileid']").attrib["value"])

            players.append(Player(name=name, killed_by_me=killed_by_me, killed_me=killed_me, mmr=player_mmr,
                                  profile_id=profile_id))

        assert len(players) == number_of_players, "Mismatch between the number of parsed players and the expected " \
                                                  "number of players. "
        teams.append(Team(randoms=randoms, mmr=team_mmr, own_team=own_team, players=tuple(players)))
    return tuple(teams)
