from __future__ import annotations

from dataclasses import dataclass

from colorama import Fore, Style

from ..formats import format_mmr
from .xml.serializable import Serializable, XmlElement
from .xml.elements import append_element, get_element_value


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
        kill_count: str = f" {self.killed_by_me}x" if self.killed_by_me > 1 else ""
        return f"Killed {self.format_name()}{kill_count}"

    def format_deaths(self) -> str:
        """
        Generate a formatted name with the amount of times this player killed the local player.
        :return: a color formatted string
        """
        death_count: str = f" {self.killed_me}x" if self.killed_me > 1 else ""
        return f"Died to {self.format_name(color_prefix=Fore.RED)}{death_count}"

    # Serialization
    @staticmethod
    def _generate_prefix(team_id: int, player_id: int) -> str:
        """
        Generate a prefix for the class.
        :param team_id: the team id of the player
        :param player_id: the id of the player
        :return: a MissionBagPlayer prefix
        """
        return f"MissionBagPlayer_{team_id}_{player_id}"

    # noinspection PyMethodOverriding
    def serialize(self, root: XmlElement, *, team_id: int, player_id: int) -> None:  # type: ignore
        """
        Serializes a Player class instance.
        :param root: the root element to serialize into
        :param team_id: the team id of the player
        :param player_id: the id of the player
        """
        # Generate the prefix
        prefix: str = Player._generate_prefix(team_id, player_id)

        # Append the elements
        append_element(root, name=f"{prefix}_blood_line_name", value=self.name)
        append_element(root, name=f"{prefix}_bountyextracted", value=self.bounties_extracted)
        append_element(root, name=f"{prefix}_bountypickedup", value=self.bounties_picked_up)
        append_element(root, name=f"{prefix}_downedbyme", value=self.downed_by_me)
        append_element(root, name=f"{prefix}_downedbyteammate", value=self.downed_by_teammate)
        append_element(root, name=f"{prefix}_downedme", value=self.downed_me)
        append_element(root, name=f"{prefix}_downedteammate", value=self.downed_teammate)
        append_element(root, name=f"{prefix}_hadWellspring", value=self.had_wellspring)
        append_element(root, name=f"{prefix}_ispartner", value=self.is_partner)
        append_element(root, name=f"{prefix}_issoulsurvivor", value=self.is_soul_survivor)
        append_element(root, name=f"{prefix}_killedbyme", value=self.killed_by_me)
        append_element(root, name=f"{prefix}_killedbyteammate", value=self.killed_by_teammate)
        append_element(root, name=f"{prefix}_killedme", value=self.killed_me)
        append_element(root, name=f"{prefix}_killedteammate", value=self.killed_teammate)
        append_element(root, name=f"{prefix}_mmr", value=self.mmr)
        append_element(root, name=f"{prefix}_profileid", value=self.profile_id)
        append_element(root, name=f"{prefix}_proximitytome", value=self.proximity_to_me)
        append_element(root, name=f"{prefix}_proximitytoteammate", value=self.proximity_to_teammate)
        append_element(root, name=f"{prefix}_skillbased", value=self.skillbased)
        append_element(root, name=f"{prefix}_teamextraction", value=self.team_extraction)

    # noinspection PyMethodOverriding
    @staticmethod
    def deserialize(root: XmlElement, *, team_id: int, player_id: int) -> Player:  # type: ignore
        """
        Deserialize a series of elements into a Player instance.
        :return: a serialized Player instance
        """
        # Generate the prefix
        prefix: str = Player._generate_prefix(team_id, player_id)

        # Parse the values
        name: str = get_element_value(root, f"{prefix}_blood_line_name")
        bounties_extracted: int = get_element_value(root, f"{prefix}_bountyextracted", result_type=int)
        bounties_picked_up: int = get_element_value(root, f"{prefix}_bountypickedup", result_type=int)
        downed_by_me: int = get_element_value(root, f"{prefix}_downedbyme", result_type=int)
        downed_by_teammate: int = get_element_value(root, f"{prefix}_downedbyteammate", result_type=int)
        downed_me: int = get_element_value(root, f"{prefix}_downedme", result_type=int)
        downed_teammate: int = get_element_value(root, f"{prefix}_downedteammate", result_type=int)
        had_wellspring: bool = get_element_value(root, f"{prefix}_hadWellspring", result_type=bool)
        is_partner: bool = get_element_value(root, f"{prefix}_ispartner", result_type=bool)
        is_soul_survivor: bool = get_element_value(root, f"{prefix}_issoulsurvivor", result_type=bool)
        killed_by_me: int = get_element_value(root, f"{prefix}_killedbyme", result_type=int)
        killed_by_teammate: int = get_element_value(root, f"{prefix}_killedbyteammate", result_type=int)
        killed_me: int = get_element_value(root, f"{prefix}_killedme", result_type=int)
        killed_teammate: int = get_element_value(root, f"{prefix}_killedteammate", result_type=int)
        mmr: int = get_element_value(root, f"{prefix}_mmr", result_type=int)
        profile_id: int = get_element_value(root, f"{prefix}_profileid", result_type=int)
        proximity_to_me: bool = get_element_value(root, f"{prefix}_proximitytome", result_type=bool)
        proximity_to_teammate: bool = get_element_value(root, f"{prefix}_proximitytoteammate", result_type=bool)
        skillbased: bool = get_element_value(root, f"{prefix}_skillbased", result_type=bool)
        team_extraction: bool = get_element_value(root, f"{prefix}_teamextraction", result_type=bool)

        # Return a Player instance
        return Player(name, bounties_extracted, bounties_picked_up, downed_by_me, downed_by_teammate,
                      downed_me, downed_teammate, had_wellspring, is_partner, is_soul_survivor,
                      killed_by_me, killed_by_teammate, killed_me, killed_teammate, mmr, profile_id,
                      proximity_to_me, proximity_to_teammate, skillbased, team_extraction)
