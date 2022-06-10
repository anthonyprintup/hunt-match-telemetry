from dataclasses import dataclass
from .entry import Entry
from .team import Team


@dataclass(frozen=True)
class Match:
    player_name: str
    hunter_survived: bool
    is_quickplay: bool
    entries: tuple[Entry]
    teams: tuple[Team]
