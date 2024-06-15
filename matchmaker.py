from dataclasses import dataclass
from config import Config
import uuid
from datetime import datetime

@dataclass
class BattleConfig:
    seed: int
    level: int
    # player ids
    p0: int
    p1: int
    p2: int
    id: str # battle uuid
    date: datetime | None = None # battle created time


def make_round_robin(config: Config) -> list[BattleConfig]:
    '''
    m 人のプレイヤーで 総当たり戦
    各試合の組合せを持つ BattleConfig を返す
    '''
    res: list[BattleConfig] = []
    n = config.games
    m = len(config.players)
    seed_start = config.seed
    for i in range(m):
        for j in range(i+1, m):
            for k in range(j+1, m):
                for g in range(n):
                    seed = seed_start + g
                    res += [BattleConfig(seed, config.level, i, j, k, id=uuid.uuid4().hex)]
    return res

def make_one_vs_all(config: Config) -> list[BattleConfig]:
    '''
    player-0 vs all
    '''
    res: list[BattleConfig] = []
    n = config.games
    m = len(config.players)
    seed_start = config.seed
    i = 0
    for j in range(m):
        for k in range(j+1, m):
            for g in range(n):
                seed = seed_start + g
                res += [BattleConfig(seed, config.level, i, j, k, id=uuid.uuid4().hex)]
    return res


def pack_args(arr: list[BattleConfig], pack_size: int) -> list[list[BattleConfig]]:
    '''
    BattleConfig のリストを pack_size で分ける
    '''
    res = [arr[i:i+pack_size] for i in range(0, len(arr), pack_size)]
    return res

def make_match(config: Config) -> list[BattleConfig]:
    '''
    config.mode に基づいて全試合の組み合わせを作ってそのリストを返す
    '''
    if config.mode == 'all':
        return make_round_robin(config)
    if config.mode == 'vs0':
        return make_one_vs_all(config)
    raise ValueError(f"invalid config.mode value: `{config.mode}`")
    return []