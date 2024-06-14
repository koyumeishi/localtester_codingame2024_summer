from multiprocessing import Value, Lock
from abc import ABC, abstractmethod
from config import Config


class AbstractMatchManager(ABC):
    @abstractmethod
    def __init__(self, config: Config):
        pass

    @abstractmethod
    def get_next_match(self) -> tuple[int, tuple[int, int]]:
        # 次の試合を取得する処理
        pass

    @abstractmethod
    def store_match_result(self, seed: int, pair: tuple[int, int], result: str):
        # 途中の試合結果を保存する処理
        pass

    @abstractmethod
    def get_num_matches(self) -> int:
        pass

    @abstractmethod
    def get_config(self) -> Config:
        pass


class MatchManager_all(AbstractMatchManager):
    def __init__(self, config: Config):
        self.config = config
        self.lock = Lock()
        self.index = Value('i', 0, lock=False)
        n = len(config.players)
        # (i, j) where i<j
        match_pairs = [[(i, j) for j in range(i+1, n)] for i in range(n)]
        match_pairs = [q for p in match_pairs for q in p * 3]  # flatten
        self.match_list = match_pairs
        self.num_matchs = len(self.match_list) * config.games

    def get_next_match(self) -> tuple[int, tuple[int, int]]:
        with self.lock:
            i: int = self.index.value
            assert i < self.num_matchs
            n = len(self.match_list)
            loops: int = i // n
            seed: int = self.config.seed + loops
            pair: tuple[int, int] = self.match_list[i % n]
            self.index.value += 1
        return seed, pair

    def store_match_result(self, seed: int, pair: tuple[int, int], result: str):
        with self.lock:
            pass

    def get_num_matches(self) -> int:
        return self.num_matchs

    def get_config(self) -> Config:
        return self.config


class MatchManager_vs0(AbstractMatchManager):
    def __init__(self, config: Config):
        self.config = config
        self.lock = Lock()
        self.index = Value('i', 0, lock=False)
        n = len(config.players)
        # (0, j) where 0<j
        match_pairs = [(int(0), j) for j in range(1, n)]
        self.match_list = match_pairs
        self.num_matchs = len(self.match_list) * config.games

    def get_next_match(self) -> tuple[int, tuple[int, int]]:
        with self.lock:
            i: int = self.index.value
            assert i < self.num_matchs
            n = len(self.match_list)
            loops = i // n
            seed = self.config.seed + loops
            pair = self.match_list[i % n]
            self.index.value += 1
        return seed, pair

    def store_match_result(self, seed: int, pair: tuple[int, int], result: str):
        with self.lock:
            pass

    def get_num_matches(self) -> int:
        return self.num_matchs

    def get_config(self) -> Config:
        return self.config