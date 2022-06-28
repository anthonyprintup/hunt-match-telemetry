from dataclasses import dataclass
from .player import Player


@dataclass(frozen=True)
class Team:
    randoms: bool
    mmr: int
    own_team: bool
    players: tuple[Player]
