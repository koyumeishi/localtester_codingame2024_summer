from dataclasses import dataclass, field
from serde import serde


@serde
@dataclass
class Player:
    name: str = "Player"
    exec: str = ""
    description: str = ""


@serde
@dataclass
class Config:
    level: int = 1
    threads: int = 1
    seed: int = 1
    games: int = 1
    description: str = ""
    mode: str = "vs0"
    players: list[Player] = field(default_factory=list)
