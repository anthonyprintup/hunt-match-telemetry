from dataclasses import dataclass


@dataclass(frozen=True)
class Rewards:
    bounty: int
    xp: int
    hunt_dollars: int
    bloodbonds: int
    hunter_xp: int
    hunter_levels: int
    upgrade_points: int
    bloodline_xp: int
