from matchmaker import BattleConfig
from config import Config
from datetime import datetime
from sqlalchemy import ForeignKey, create_engine, Column, String, DateTime, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from serde.yaml import to_yaml
from game import get_game_ranks, get_game_scores
import json

# SQLiteデータベースの作成
engine = create_engine('sqlite:///database.db')
Base = declarative_base()

class Round(Base):
    '''
    一つの Config での試合を 1 round として管理
    '''
    __tablename__ = 'round'

    id = Column(String, primary_key=True)
    date = Column(DateTime)
    config = Column(String)


class GameResult(Base):
    '''
    試合結果の情報
    '''
    __tablename__ = 'match_result'

    id = Column(String, primary_key=True)
    date = Column(DateTime)
    round_id = Column(String, ForeignKey("round.id"))
    # 試合のデータ
    result_json = Column(String)
    player_id_0 = Column(Integer)
    player_id_1 = Column(Integer)
    player_id_2 = Column(Integer)
    player_name_0 = Column(String)
    player_name_1 = Column(String)
    player_name_2 = Column(String)
    rank_0 = Column(Integer) # rank of player 0
    rank_1 = Column(Integer)
    rank_2 = Column(Integer)
    pending = Column(Boolean)  # pending
    seed = Column(Integer)


# テーブルの作成
Base.metadata.create_all(bind=engine)

# セッションの作成
Session = sessionmaker(bind=engine)
session = Session()

def make_new_round(config: Config, matches: list[BattleConfig]):
    '''
    1 ラウンドの全試合の情報をデータベースへ登録 (試合は未実行)
    '''
    round_id = uuid.uuid4().hex
    round_data = Round(id=round_id, date=datetime.now(),
                       config=to_yaml(config))
    session.add(round_data)

    # 試合前の空のデータを登録
    m = [GameResult(
        id=args.id,
        round_id=round_id,
        player_id_0=args.p0,
        player_id_1=args.p1,
        player_id_2=args.p2,
        player_name_0=config.players[args.p0].name,
        player_name_1=config.players[args.p1].name,
        player_name_2=config.players[args.p2].name,
        pending=True,
        rank_0=0, rank_1=0, rank_2=0,
        seed=args.seed) for args in matches]
    session.bulk_save_objects(m)
    session.commit()
    return round_id


def update_match_results(results: list[tuple[BattleConfig, str]]):
    '''
    試合の結果を更新する
    (BattleConfig, 試合の情報のjson string)
    '''
    n = len(results)
    m = []
    
    for (args, json) in results:
        ranks = get_game_ranks(json)
        data = dict(id=args.id, date=args.date,
                    pending=False, rank_0=ranks[0], rank_1=ranks[1], rank_2=ranks[2], result_json=json)
        m += [data]
    session.bulk_update_mappings(GameResult, m)
    session.commit()


def get_round_list():
    '''
    全ラウンド (1 ラウンドは一つの Config による試合の集合) のリストを取得
    '''
    res = session.query(Round).order_by(Round.date.desc()).all()
    return res


def get_game_results_list(round_id: str | None) -> list[GameResult] | None:
    '''
    round_id に属する試合結果を取得
    '''
    if round_id is None:
        return None
    res = session.query(GameResult).filter(
        GameResult.round_id == round_id).order_by(GameResult.date.desc()).all()
    return res

def get_config_yaml(round_id: str) :
    '''
    round_id に使われた config を取得
    '''
    res = session.query(Round.config).filter(Round.id == round_id).all()
    if len(res) == 0:
        return None
    return res[0].config # type: ignore

def get_game_json(game_id: str):
    '''
    game_id の試合を取得
    '''
    res = session.query(GameResult.result_json).filter(GameResult.id == game_id).all()
    if len(res) == 0:
        return None
    return res[0].result_json # type: ignore
