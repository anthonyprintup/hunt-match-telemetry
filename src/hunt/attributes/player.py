from dataclasses import dataclass

from colorama import Fore, Style

from ..formats import format_mmr


@dataclass(frozen=True)
class Player:
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
