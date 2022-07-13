from dataclasses import dataclass
from .player import Player


@dataclass(frozen=True)
class Team:
    handicap: int
    is_invite: bool
    mmr: int
    own_team: bool
    players: tuple[Player, ...]
