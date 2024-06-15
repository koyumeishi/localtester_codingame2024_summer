from dataclasses import dataclass, field
from serde import serde

# player 用のデータ型
# 名前, 実行コマンド, その他記述
@serde
@dataclass
class Player:
    name: str = "Player"
    exec: str = ""
    description: str = ""


# 設定用データ型
# 全ての試合で共通した設定が使われる
# level (leagueによる差異)
# threads (使うスレッド数)
# seed 試合のシード値
# games 試合数
# mode 組合せ決定のモード
# players プレイヤーの設定
@serde
@dataclass
class Config:
    level: int = 1
    threads: int = 1
    seed: int = 1
    games: int = 1
    description: str = ""
    mode: str = "all"
    players: list[Player] = field(default_factory=list)
