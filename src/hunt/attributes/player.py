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


@dataclass(frozen=True)
class TestServerPlayer:
    name: str
    bounties_extracted: int
    bounties_picked_up: int
    downed_by_me: int
    downed_by_teammate: int
    downed_me: int
    downed_teammate: int
    had_wellspring: bool
    is_partner: bool
    is_soul_survivor: bool
    killed_by_me: int
    killed_by_teammate: int
    killed_me: int
    killed_teammate: int
    mmr: int
    profile_id: int
    proximity_to_me: bool
    proximity_to_teammate: bool
    skillbased: bool
    team_extraction: bool
