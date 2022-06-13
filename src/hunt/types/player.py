from dataclasses import dataclass


@dataclass(frozen=True)
class Player:
    name: str
    had_wellspring: bool
    had_bounty: bool
    killed_by_me: int
    killed_me: int
    mmr: int
    profile_id: int
    used_proximity_chat: bool
    is_skillbased: bool
