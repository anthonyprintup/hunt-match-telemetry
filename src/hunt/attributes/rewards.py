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
    event_points: int

    def __bool__(self) -> bool:
        """
        Override the bool method to check if there were any rewards.
        :return: True if the match had rewards otherwise False
        """
        return any(variable_value for variable_value in vars(self).values())
