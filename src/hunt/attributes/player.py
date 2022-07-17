from __future__ import annotations

from dataclasses import dataclass

from colorama import Fore, Style

from .xml.serializable import MappingGenerator, Serializable, XmlElement
from ..formats import format_mmr


@dataclass(frozen=True)
class Player(Serializable):
    name: str
    bounties_extracted: int
    bounties_picked_up: int
    downed_by_me: int
    downed_by_teammate: int
    downed_me: int
    downed_teammate: int
    had_wellspring: bool
    is_partner: bool
    is_soul_survivor: bool
    killed_by_me: int
    killed_by_teammate: int
    killed_me: int
    killed_teammate: int
    mmr: int
    profile_id: int
    proximity_to_me: bool
    proximity_to_teammate: bool
    skillbased: bool
    team_extraction: bool

    # Formatting
    def format_name(self, color_prefix: str = Fore.GREEN, is_local_player: bool = False) -> str:
        """
        Generate a formatted name.
        :param color_prefix: the color to prefix the name with
        :param is_local_player: the Player instance is the instance of the local player
        :return: a color formatted string
        """
        local_player_marker: str = " (you)" if is_local_player else ""
        return f"{color_prefix}{self.name}{Style.RESET_ALL} ({format_mmr(self.mmr)}){local_player_marker}"

    def format_kills(self) -> str:
        """
        Generate a formatted name with the amount of times this player was killed by the local player.
        :return: a color formatted string
        """
        kills: int = self.downed_by_me + self.killed_by_me
        kill_count: str = f" {kills}x" if kills > 1 else ""
        return f"Killed {self.format_name()}{kill_count}"

    def format_deaths(self) -> str:
        """
        Generate a formatted name with the amount of times this player killed the local player.
        :return: a color formatted string
        """
        deaths: int = self.downed_me + self.killed_me
        death_count: str = f" {deaths}x" if deaths > 1 else ""
        return f"Died to {self.format_name(color_prefix=Fore.RED)}{death_count}"

    # Serialization
    @staticmethod
    def _generate_prefix(team_id: int, player_id: int) -> str:
        """
        Generate a prefix for the class.
        :param team_id: the team id of the player's team
        :param player_id: the id of the player
        :return: a MissionBagPlayer prefix
        """
        return f"MissionBagPlayer_{team_id}_{player_id}"

    # noinspection PyMethodOverriding
    @staticmethod
    def _data_mappings() -> MappingGenerator:
        """
        Yield each variable name and its corresponding attribute suffix.
        :return: a generator which yields the name, value
        """
        # Yield the values
        yield "name", "blood_line_name"
        yield "bounties_extracted", "bountyextracted"
        yield "bounties_picked_up", "bountypickedup"
        yield "downed_by_me", "downedbyme"
        yield "downed_by_teammate", "downedbyteammate"
        yield "downed_me", "downedme"
        yield "downed_teammate", "downedteammate"
        yield "had_wellspring", "hadWellspring"
        yield "is_partner", "ispartner"
        yield "is_soul_survivor", "issoulsurvivor"
        yield "killed_by_me", "killedbyme"
        yield "killed_by_teammate", "killedbyteammate"
        yield "killed_me", "killedme"
        yield "killed_teammate", "killedteammate"
        yield "mmr", "mmr"
        yield "profile_id", "profileid"
        yield "proximity_to_me", "proximitytome"
        yield "proximity_to_teammate", "proximitytoteammate"
        yield "skillbased", "skillbased"
        yield "team_extraction", "teamextraction"

    # noinspection PyMethodOverriding
    def serialize(self, root: XmlElement, *, team_id: int, player_id: int) -> None:  # type: ignore[override]
        """
        Serialize a Player instance.
        :param root: the root element to serialize into
        :param team_id: the team id of the player
        :param player_id: the id of the player
        """
        # Generate the prefix
        prefix: str = Player._generate_prefix(team_id, player_id)

        # Serialize the data
        super().serialize(root, prefix)

    # noinspection PyMethodOverriding
    @classmethod
    def deserialize(cls, root: XmlElement, *, team_id: int, player_id: int) -> Player:  # type: ignore[override]
        """
        Deserialize a series of elements into a Player instance.
        :return: a serialized Player instance
        """
        # Generate the prefix
        prefix: str = Player._generate_prefix(team_id, player_id)

        # Deserialize the data
        return super(cls, cls).deserialize(root, prefix)
