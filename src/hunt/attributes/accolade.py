from dataclasses import dataclass


@dataclass(frozen=True)
class Accolade:
    bloodline_xp: int
    bounty: int
    category: str
    event_points: int
    bloodbonds: int
    generated_bloodbonds: int
    hunt_dollars: int
    hits: int
    hunter_points: int
    hunter_xp: int
    weighting: int
    xp: int
