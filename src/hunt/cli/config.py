from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    debug: bool
    test_server: bool
    statistics: bool
