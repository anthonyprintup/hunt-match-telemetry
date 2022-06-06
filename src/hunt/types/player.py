from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Player:
    name: str
    killed_by_me: bool
    killed_me: bool
    mmr: int
    profile_id: int
