from dataclasses import dataclass


@dataclass(frozen=True)
class Accolade:
    amount: int
    category: str
    descriptor_name: str
    descriptor_score: int
    descriptor_type: int
    reward_type: int
    reward_size: int
