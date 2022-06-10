from dataclasses import dataclass


@dataclass(frozen=True)
class Entry:
    amount: int
    category: str
    descriptor_name: str
    descriptor_score: str
    descriptor_type: str
    reward_type: int
    reward_size: int
