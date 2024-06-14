from dataclasses import dataclass
from config import Config
import uuid
from datetime import datetime

@dataclass
class MatchArgs:
    seed: int
    level: int
    p0: int
    p1: int
    id: str
    date: datetime | None = None


def make_vs0(config: Config) -> list[MatchArgs]:
    res: list[MatchArgs] = []
    n = config.games
    m = len(config.players)
    s0 = config.seed
    i = 0
    for j in range(i+1, m):
        for g in range(n):
            res += [MatchArgs(s0 + g, config.level, i, j, id=uuid.uuid4().hex)]
    return res


def make_round_robin(config: Config) -> list[MatchArgs]:
    res: list[MatchArgs] = []
    n = config.games
    m = len(config.players)
    s0 = config.seed
    for i in range(m):
        for j in range(i+1, m):
            for g in range(n):
                res += [MatchArgs(s0 + g, config.level, i, j, id=uuid.uuid4().hex)]
    return res


def pack_args(arr: list[MatchArgs], pack_size: int) -> list[list[MatchArgs]]:
    res = [arr[i:i+pack_size] for i in range(0, len(arr), pack_size)]
    return res

def make_match(config: Config) -> list[MatchArgs]:
    if config.mode == 'all':
        return make_round_robin(config)
    elif config.mode == 'vs0':
        return make_vs0(config)
    raise ValueError(f"invalid config.mode value: `{config.mode}`")
    return []