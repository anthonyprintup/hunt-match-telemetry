import builtins
import random
import string
from datetime import datetime
from pathlib import Path
from typing import Any, Generator
from unittest.mock import MagicMock, mock_open as unittest_mock_open

from colorama import Fore, Style
from pytest import MonkeyPatch, fixture

from hunt.attributes.match import Accolade, Entry, Match, Rewards, Team
from hunt.attributes.team import Player, SerializableTeam
from hunt.attributes.xml.elements import XmlElement, append_element
from hunt.constants import MATCH_LOGS_PATH
from hunt.formats import format_mmr

MAGIC_FILE_PATH: Path = Path(f"dummy_path_{''.join(random.choice(string.ascii_letters) for _ in range(16))}")


# noinspection PyUnusedLocal
def mock_match_generate_file_path(self: Match, time: datetime | None = None) -> Path:
    """
    Mock Match.generate_file_path
    :param self: a Match instance
    :param time: the time to use in this context
    :return: a dummy file path
    """
    return MAGIC_FILE_PATH


# noinspection PyUnusedLocal
def mock_path_mkdir(*args: Any, **kwargs: Any) -> None: ...


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
    assert not (is_quickplay and is_partner), "is_partner cannot be True when is_quickplay is True."
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
    profile_id: int = int(abs(random.gauss(10 ** 8, 10 ** 10)))
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
def static_time() -> datetime:
    """
    Generate a static datetime result.
    :return: a datetime instance
    """
    return datetime(year=2000, month=12, day=25)


@fixture(scope="module")
def expected_match() -> Match:
    """
    The expected parsing result.
    :return: a Match instance
    """
    # Return a Match instance
    local_player: Player = _generate_player("Player")
    return Match(player_name=local_player.name, bloodline_rank=100, is_hunter_dead=False, is_quickplay=False,
                 region="eu", secondary_region="",
                 accolades=(Accolade(0, 0, "accolade_extraction", 0, 0, 10, 0, 0, 0, 0, 0, 0),
                            Accolade(0, 0, "accolade_gained_serpent2022_event_points", 200, 0, 0, 0, 0, 0, 0, 0, 0),),
                 entries=(
                     # bounty
                     Entry(amount=30, category="accolade_clues_found", descriptor_name="found spider clue 1st",
                           descriptor_score=1, descriptor_type=7, reward_type=0, reward_size=1500),
                     # xp
                     Entry(amount=1000, category="accolade_monsters_killed", descriptor_name="kill grunt",
                           descriptor_score=1, descriptor_type=2, reward_type=2, reward_size=10000),
                     # hunt dollars
                     Entry(amount=40, category="accolade_found_gold", descriptor_name="loot gold",
                           descriptor_score=0, descriptor_type=0, reward_type=4, reward_size=500),
                     # hunter xp
                     Entry(amount=2, category="UNKNOWN", descriptor_name="loot hunter xp",
                           descriptor_score=0, descriptor_type=0, reward_type=10, reward_size=2000),
                     # hunter levels
                     Entry(amount=1, category="accolade_hunter_points", descriptor_name="hunter points",
                           descriptor_score=1, descriptor_type=0, reward_type=0, reward_size=38),
                     # upgrade points
                     Entry(amount=1, category="UNKNOWN", descriptor_name="loot upgrade points",
                           descriptor_score=0, descriptor_type=0, reward_type=11, reward_size=4),
                     # bloodline xp
                     Entry(amount=1, category="UNKNOWN", descriptor_name="loot bloodline xp",
                           descriptor_score=0, descriptor_type=0, reward_type=12, reward_size=500)),
                 rewards=Rewards(bounty=1500, xp=12000, hunt_dollars=600, bloodbonds=10, hunter_xp=2000,
                                 hunter_levels=38, upgrade_points=4, bloodline_xp=500, event_points=200),
                 teams=(Team(handicap=0, is_invite=True, mmr=3000, own_team=True,
                             players=(local_player, _generate_player("Ada", is_partner=True),
                                      _generate_player("Henry", is_partner=True))),
                        Team(handicap=0, is_invite=True, mmr=2500, own_team=False,
                             players=(_generate_player("Jerry"), _generate_player("Jonathan"),
                                      _generate_player("Josh")))))


@fixture
def mock_open() -> MagicMock:
    """
    Mock builtins.open.
    :return: a MagicMock instance
    """
    return unittest_mock_open()


@fixture
def io_safe_match(expected_match: Match,
                  monkeypatch_module_scope: MonkeyPatch, mock_open: MagicMock) -> Generator[Match, None, None]:
    """
    Wrap a Match instance with IO patches to avoid modifying the filesystem running our tests.
    :param expected_match: a populated Match instance
    :param monkeypatch_module_scope: a MonkeyPatch instance
    :param mock_open: a MagicMock instance for mocking builtins.open
    :return: an IO safe Match instance
    """
    monkeypatch_context: MonkeyPatch
    with monkeypatch_module_scope.context() as monkeypatch_context:
        # Set up the patches
        monkeypatch_context.setattr(Match, "generate_file_path", mock_match_generate_file_path)
        monkeypatch_context.setattr(Path, "mkdir", mock_path_mkdir)
        monkeypatch_context.setattr(builtins, "open", mock_open)

        # Yield the match
        yield expected_match


@fixture
def expected_file_path(expected_match: Match, static_time: datetime) -> Path:
    """
    Generate the file path that's expected to be generated by Match.generate_file_path.
    :param expected_match: a Match instance
    :param static_time: a static datetime value
    :return: the expected file path
    """
    return MATCH_LOGS_PATH / f"{static_time.year}-{static_time.month:02d}-{static_time.day:02d}" / (
        "quickplay" if expected_match.is_quickplay else "bounty_hunt") / (
        f"{static_time.hour:02d}-{static_time.minute:02d}-{static_time.second:02d}.json")


@fixture
def attributes_tree(expected_match: Match) -> XmlElement:
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
    hunt_dollar_bonus: int = int(hunt_dollars - hunt_dollars * bonus_multiplier ** -1)
    xp_bonus: int = int(xp - xp * bonus_multiplier ** -1)

    append_element(attributes, name="MissionBagFbeGoldBonus", value=hunt_dollar_bonus)
    append_element(attributes, name="MissionBagFbeHunterXpBonus", value=xp_bonus)

    # Other information
    append_element(attributes, name="Unlocks/UnlockRank", value=100)
    append_element(attributes, name="MissionBagIsHunterDead", value=expected_match.is_hunter_dead)
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
        serializable_team: SerializableTeam = team.to_serializable_team()
        serializable_team.serialize(attributes, team_id=i)

    # Region information
    append_element(attributes, name="Region", value="eu")
    append_element(attributes, name="SecondaryRegion", value="")

    # Return the attribute tree
    return attributes


@fixture
def mocked_player(monkeypatch: MonkeyPatch) -> Generator[Player, None, None]:
    """
    Wrap a Player instance with colorama patches to avoid having to match colors when testing formats.
    :param monkeypatch: a MonkeyPatch instance
    :return: a mocked Player instance
    """
    # Generate a player
    player: Player = _generate_player("Person")

    monkeypatch_context: MonkeyPatch
    with monkeypatch.context() as monkeypatch_context:
        # Set up the patches
        monkeypatch_context.setattr(Player.format_name, "__defaults__", ("", False))
        for key_name in vars(Fore).keys():
            monkeypatch_context.setattr(Fore, key_name, "")
        for key_name in vars(Style).keys():
            monkeypatch_context.setattr(Style, key_name, "")

        # Yield the player
        yield player


@fixture
def expected_name_prefix(mocked_player: Player) -> str:
    """
    Generate the expected result from Player.format_name().
    :param mocked_player: a mocked Player instance
    :return: the expected result
    """
    return f"{mocked_player.name} ({format_mmr(mocked_player.mmr)})"
