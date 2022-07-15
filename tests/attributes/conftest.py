import random
from typing import Generator
from xml.etree.ElementTree import Element as XmlElement

from pytest import fixture

from hunt.attributes.match import Match, Accolade, Entry, Rewards, Team, Player


def _create_element(tag: str, attributes: dict[str, str]) -> XmlElement:
    """
    A helper function which creates a new element.
    :param tag: the tag to use
    :param attributes: the attributes to apply to the element
    :return: an XmlElement instance
    """
    return XmlElement(tag, attrib=attributes)


def _append_attribute(element: XmlElement, name: str, value: str) -> None:
    """
    A helper function which appends a new element to an existing element.
    :param element: the element to append to
    :param name: the name of the attribute
    :param value: the value of the attribute
    """
    new_element: XmlElement = _create_element(tag="Attr", attributes={"name": name, "value": value})
    element.append(new_element)


def _generate_player(name: str, is_quickplay: bool = False, is_partner: bool = False) -> Player:
    """
    A helper function which generates a new Player instance with random (but sensible) data.
    :param name: the name of the player
    :param is_quickplay: True if the match was a quickplay match
    :param is_partner: True if the player is a partner
    :return: a new Player instance
    """
    # Quickplay-specific checks and limits
    if is_quickplay:
        assert not is_partner, "is_partner cannot be True when is_quickplay is True."
    kills_deaths_upper_limit: int = 5 if not is_quickplay else 1

    # Variables
    bounties_picked_up: int = int(random.gauss(1, 1)) if not is_quickplay else 0
    bounties_extracted: int = bounties_picked_up if not is_quickplay else 0
    downed_by_me: int = random.randint(0, kills_deaths_upper_limit)
    downed_by_teammate: int = random.randint(0, kills_deaths_upper_limit)
    downed_me: int = random.randint(0, kills_deaths_upper_limit)
    downed_teammate: int = random.randint(0, kills_deaths_upper_limit)
    had_wellspring: bool = bool(random.getrandbits(1)) if is_quickplay else False
    is_soul_survivor: bool = had_wellspring and bool(random.getrandbits(1))
    killed_by_me: int = random.randint(0, kills_deaths_upper_limit) if not is_partner else 0
    killed_by_teammate: int = random.randint(0, kills_deaths_upper_limit) if not is_partner else 0
    killed_me: int = random.randint(0, kills_deaths_upper_limit) if not is_partner else 0
    killed_teammate: int = random.randint(0, kills_deaths_upper_limit) if not is_partner else 0
    mmr: int = int(random.gauss(2695, 600))
    profile_id: int = int(abs(random.gauss(10**8, 10**10)))
    proximity_to_me: bool = bool(random.getrandbits(1))
    proximity_to_teammate: bool = bool(random.getrandbits(1))
    skillbased: bool = bool(random.getrandbits(1)) if not is_quickplay else False
    team_extraction: bool = bool(random.getrandbits(1)) if (
            not (killed_by_me or killed_by_teammate) and not is_quickplay) else False

    return Player(name, bounties_extracted, bounties_picked_up, downed_by_me, downed_by_teammate,
                  downed_me, downed_teammate, had_wellspring, is_partner, is_soul_survivor,
                  killed_by_me, killed_by_teammate, killed_me, killed_teammate, mmr, profile_id,
                  proximity_to_me, proximity_to_teammate, skillbased, team_extraction)


@fixture(scope="session")
def expected_match() -> Generator[Match, None, None]:
    """
    The expected parsing result.
    :return: a Match instance
    """
    local_player: Player = _generate_player("Player")
    yield Match(player_name=local_player.name, hunter_survived=True, is_quickplay=False,
                accolades=(Accolade(0, 0, "accolade_extraction", 0, 0, 10, 0, 0, 0, 0, 0, 0),),
                entries=(Entry(amount=30, category="accolade_clues_found", descriptor_name="found spider clue 1st",
                               descriptor_score=1, descriptor_type=7, reward_type=0, reward_size=1500),  # bounty
                         Entry(amount=1000, category="accolade_monsters_killed", descriptor_name="kill grunt",  # xp
                               descriptor_score=1, descriptor_type=2, reward_type=2, reward_size=10000),
                         Entry(amount=40, category="accolade_found_gold", descriptor_name="loot gold",  # hunt dollars
                               descriptor_score=0, descriptor_type=0, reward_type=4, reward_size=500),
                         Entry(amount=2, category="UNKNOWN", descriptor_name="loot hunter xp",  # hunter xp
                               descriptor_score=0, descriptor_type=0, reward_type=10, reward_size=2000),
                         Entry(amount=1, category="accolade_hunter_points", descriptor_name="hunter points",
                               descriptor_score=1, descriptor_type=0, reward_type=0, reward_size=38),  # hunter levels
                         Entry(amount=1, category="UNKNOWN", descriptor_name="loot upgrade points",  # upgrade points
                               descriptor_score=0, descriptor_type=0, reward_type=11, reward_size=4),
                         Entry(amount=1, category="UNKNOWN", descriptor_name="loot bloodline xp",  # bloodline xp
                               descriptor_score=0, descriptor_type=0, reward_type=12, reward_size=500)),
                rewards=Rewards(bounty=1500, xp=12000, hunt_dollars=600, bloodbonds=10, hunter_xp=2000,
                                hunter_levels=38, upgrade_points=4, bloodline_xp=500),
                teams=(Team(handicap=0, is_invite=True, mmr=3000, own_team=True,
                            players=(local_player, _generate_player("Ada", is_partner=True),
                                     _generate_player("Henry", is_partner=True))),
                       Team(handicap=0, is_invite=True, mmr=2500, own_team=False,
                            players=(_generate_player("Jerry"), _generate_player("Jonathan"),
                                     _generate_player("Josh")))))


# noinspection DuplicatedCode
@fixture
def attributes_tree(expected_match: Match) -> Generator[XmlElement, None, None]:
    """
    Create a dummy attributes element tree for parsing into a Match instance.
    :return: an element tree
    """
    attributes: XmlElement = _create_element(tag="Attributes", attributes={"Version": "37"})

    # Accolades
    i: int
    accolade: Accolade
    for i, accolade in enumerate(expected_match.accolades):
        accolade_prefix: str = f"MissionAccoladeEntry_{i}"
        _append_attribute(attributes, name=f"{accolade_prefix}", value="1")
        _append_attribute(attributes, name=f"{accolade_prefix}_bloodlineXp", value=f"{accolade.bloodline_xp}")
        _append_attribute(attributes, name=f"{accolade_prefix}_bounty", value=f"{accolade.bounty}")
        _append_attribute(attributes, name=f"{accolade_prefix}_category", value=f"{accolade.category}")
        _append_attribute(attributes, name=f"{accolade_prefix}_eventPoints", value=f"{accolade.event_points}")
        _append_attribute(attributes, name=f"{accolade_prefix}_gems", value=f"{accolade.bloodbonds}")
        _append_attribute(attributes, name=f"{accolade_prefix}_generatedGems", value=f"{accolade.generated_bloodbonds}")
        _append_attribute(attributes, name=f"{accolade_prefix}_gold", value=f"{accolade.hunt_dollars}")
        _append_attribute(attributes, name=f"{accolade_prefix}_hits", value=f"{accolade.hits}")
        _append_attribute(attributes, name=f"{accolade_prefix}_hunterPoints", value=f"{accolade.hunter_points}")
        _append_attribute(attributes, name=f"{accolade_prefix}_hunterXp", value=f"{accolade.hunter_xp}")
        _append_attribute(attributes, name=f"{accolade_prefix}_weighting", value=f"{accolade.weighting}")
        _append_attribute(attributes, name=f"{accolade_prefix}_xp", value=f"{accolade.xp}")

    # Entries
    for i, entry in enumerate(expected_match.entries):
        entry_prefix: str = f"MissionBagEntry_{i}"
        _append_attribute(attributes, name=f"{entry_prefix}", value="1")
        _append_attribute(attributes, name=f"{entry_prefix}_amount", value=f"{entry.amount}")
        _append_attribute(attributes, name=f"{entry_prefix}_category", value=f"{entry.category}")
        _append_attribute(attributes, name=f"{entry_prefix}_descriptorName", value=f"{entry.descriptor_name}")
        _append_attribute(attributes, name=f"{entry_prefix}_descriptorScore", value=f"{entry.descriptor_score}")
        _append_attribute(attributes, name=f"{entry_prefix}_descriptorType", value=f"{entry.descriptor_type}")
        _append_attribute(attributes, name=f"{entry_prefix}_reward", value=f"{entry.reward_type}")
        _append_attribute(attributes, name=f"{entry_prefix}_rewardSize", value=f"{entry.reward_size}")

    # Bonuses
    hunt_dollars: int = expected_match.rewards.hunt_dollars
    xp: int = expected_match.rewards.xp

    bonus_multiplier: float = 1.0 + 20 / 100  # 20%
    hunt_dollar_bonus: int = int(hunt_dollars - hunt_dollars * bonus_multiplier**-1)
    xp_bonus: int = int(xp - xp * bonus_multiplier**-1)

    _append_attribute(attributes, name="MissionBagFbeGoldBonus", value=f"{hunt_dollar_bonus}")
    _append_attribute(attributes, name="MissionBagFbeHunterXpBonus", value=f"{xp_bonus}")

    # Other information
    _append_attribute(attributes, name="MissionBagIsHunterDead",
                      value="false" if expected_match.hunter_survived else "true")
    _append_attribute(attributes, name="MissionBagIsQuickPlay",
                      value="false" if not expected_match.is_quickplay else "true")

    # Match data
    _append_attribute(attributes, name="MissionBagNumAccolades", value=f"{len(expected_match.accolades)}")
    _append_attribute(attributes, name="MissionBagNumEntries", value=f"{len(expected_match.entries)}")
    _append_attribute(attributes, name="MissionBagNumTeams", value=f"{len(expected_match.teams)}")

    # Players
    team: Team
    player: Player
    for i, team in enumerate(expected_match.teams):
        for j, player in enumerate(team.players):
            player_prefix: str = f"MissionBagPlayer_{i}_{j}"
            _append_attribute(attributes, name=f"{player_prefix}_blood_line_name", value=f"{player.name}")
            _append_attribute(attributes, name=f"{player_prefix}_bountyextracted", value=f"{player.bounties_extracted}")
            _append_attribute(attributes, name=f"{player_prefix}_bountypickedup", value=f"{player.bounties_picked_up}")
            _append_attribute(attributes, name=f"{player_prefix}_downedbyme", value=f"{player.downed_by_me}")
            _append_attribute(attributes, name=f"{player_prefix}_downedbyteammate",
                              value=f"{player.downed_by_teammate}")
            _append_attribute(attributes, name=f"{player_prefix}_downedme", value=f"{player.downed_me}")
            _append_attribute(attributes, name=f"{player_prefix}_downedteammate", value=f"{player.downed_teammate}")
            _append_attribute(attributes, name=f"{player_prefix}_hadWellspring",
                              value=f"{str(player.had_wellspring).lower()}")
            _append_attribute(attributes, name=f"{player_prefix}_ispartner", value=f"{str(player.is_partner).lower()}")
            _append_attribute(attributes, name=f"{player_prefix}_issoulsurvivor",
                              value=f"{str(player.is_soul_survivor).lower()}")
            _append_attribute(attributes, name=f"{player_prefix}_killedbyme", value=f"{player.killed_by_me}")
            _append_attribute(attributes, name=f"{player_prefix}_killedbyteammate",
                              value=f"{player.killed_by_teammate}")
            _append_attribute(attributes, name=f"{player_prefix}_killedme", value=f"{player.killed_me}")
            _append_attribute(attributes, name=f"{player_prefix}_killedteammate", value=f"{player.killed_teammate}")
            _append_attribute(attributes, name=f"{player_prefix}_mmr", value=f"{player.mmr}")
            _append_attribute(attributes, name=f"{player_prefix}_profileid", value=f"{player.profile_id}")
            _append_attribute(attributes, name=f"{player_prefix}_proximitytome",
                              value=f"{str(player.proximity_to_me).lower()}")
            _append_attribute(attributes, name=f"{player_prefix}_proximitytoteammate",
                              value=f"{str(player.proximity_to_teammate).lower()}")
            _append_attribute(attributes, name=f"{player_prefix}_skillbased", value=f"{str(player.skillbased).lower()}")
            _append_attribute(attributes, name=f"{player_prefix}_teamextraction",
                              value=f"{str(player.team_extraction).lower()}")

    # Teams
    for i, team in enumerate(expected_match.teams):
        team_prefix: str = f"MissionBagTeam_{i}"
        _append_attribute(attributes, name=f"{team_prefix}", value="1")
        _append_attribute(attributes, name=f"{team_prefix}_handicap", value=f"{team.handicap}")
        _append_attribute(attributes, name=f"{team_prefix}_isinvite", value=f"{str(team.is_invite).lower()}")
        _append_attribute(attributes, name=f"{team_prefix}_mmr", value=f"{team.mmr}")
        _append_attribute(attributes, name=f"{team_prefix}_numplayers", value=f"{len(team.players)}")
        _append_attribute(attributes, name=f"{team_prefix}_ownteam", value=f"{str(team.own_team).lower()}")

    # Yield the attribute tree
    yield attributes
