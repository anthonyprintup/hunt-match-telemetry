from dataclasses import dataclass


@dataclass(frozen=True)
class Rewards:
    bounty: int
    hunt_dollars: int
    hunter_xp: int
