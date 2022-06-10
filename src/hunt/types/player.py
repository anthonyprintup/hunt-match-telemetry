from dataclasses import dataclass


@dataclass(frozen=True)
class Player:
    name: str
    had_wellspring: bool
    had_bounty: bool
    killed_by_me: bool
    killed_me: bool
    mmr: int
    profile_id: int
