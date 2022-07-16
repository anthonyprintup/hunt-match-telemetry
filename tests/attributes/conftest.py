import random
from typing import Generator
from xml.etree.ElementTree import Element as XmlElement

from pytest import fixture

from hunt.attributes.match import Match, Accolade, Entry, Rewards, Team, Player
from hunt.attributes.xml.elements import append_element


def _create_element(tag: str, attributes: dict[str, str]) -> XmlElement:
    """
    A helper function which creates a new element.
    :param tag: the tag to use
    :param attributes: the attributes to apply to the element
    :return: an XmlElement instance
    """
    return XmlElement(tag, attrib=attributes)


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


@fixture(scope="module")
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
    for i, accolade in enumerate(expected_match.accolades):
        accolade.serialize(attributes, accolade_id=i)

    # Entries
    for i, entry in enumerate(expected_match.entries):
        entry.serialize(attributes, entry_id=i)

    # Bonuses
    hunt_dollars: int = expected_match.rewards.hunt_dollars
    xp: int = expected_match.rewards.xp

    bonus_multiplier: float = 1.0 + 20 / 100  # 20%
    hunt_dollar_bonus: int = int(hunt_dollars - hunt_dollars * bonus_multiplier**-1)
    xp_bonus: int = int(xp - xp * bonus_multiplier**-1)

    append_element(attributes, name="MissionBagFbeGoldBonus", value=hunt_dollar_bonus)
    append_element(attributes, name="MissionBagFbeHunterXpBonus", value=xp_bonus)

    # Other information
    append_element(attributes, name="MissionBagIsHunterDead", value=not expected_match.hunter_survived)
    append_element(attributes, name="MissionBagIsQuickPlay", value=expected_match.is_quickplay)

    # Match data
    append_element(attributes, name="MissionBagNumAccolades", value=len(expected_match.accolades))
    append_element(attributes, name="MissionBagNumEntries", value=len(expected_match.entries))
    append_element(attributes, name="MissionBagNumTeams", value=len(expected_match.teams))

    # Players
    team: Team
    player: Player
    for i, team in enumerate(expected_match.teams):
        for j, player in enumerate(team.players):
            player.serialize(attributes, team_id=i, player_id=j)

    # Teams
    for i, team in enumerate(expected_match.teams):
        team_prefix: str = f"MissionBagTeam_{i}"
        append_element(attributes, name=f"{team_prefix}_handicap", value=team.handicap)
        append_element(attributes, name=f"{team_prefix}_isinvite", value=team.is_invite)
        append_element(attributes, name=f"{team_prefix}_mmr", value=team.mmr)
        append_element(attributes, name=f"{team_prefix}_numplayers", value=len(team.players))
        append_element(attributes, name=f"{team_prefix}_ownteam", value=team.own_team)

    # Yield the attribute tree
    yield attributes
