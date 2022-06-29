from dataclasses import dataclass


@dataclass(frozen=True)
class Rewards:
    bounty: int
    xp: int
    hunt_dollars: int
    bloodbonds: int
    hunter_xp: int
    upgrade_points: int
    bloodline_xp: int
