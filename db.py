from matchmaker import MatchArgs
from config import Config
from datetime import datetime
from sqlalchemy import ForeignKey, create_engine, Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from serde.yaml import to_yaml
from game import get_game_scores
import json

# SQLiteデータベースの作成
engine = create_engine('sqlite:///database.db')
Base = declarative_base(bind=engine)


class Round(Base):
    __tablename__ = 'round'

    id = Column(String, primary_key=True)
    date = Column(DateTime)
    config = Column(String)


class MatchResult(Base):
    __tablename__ = 'match_result'

    id = Column(String, primary_key=True)
    date = Column(DateTime)
    round_id = Column(String, ForeignKey("round.id"))
    result_json = Column(String)
    player_id_0 = Column(Integer)
    player_id_1 = Column(Integer)
    player_name_0 = Column(String)
    player_name_1 = Column(String)
    status = Column(Integer)  # -1: pending, 0/1: winner, 2: tie
    seed = Column(Integer)


# テーブルの作成
Base.metadata.create_all()

# セッションの作成
Session = sessionmaker(bind=engine)
session = Session()


def make_new_round(config: Config, matches: list[MatchArgs]):
    round_id = uuid.uuid4().hex
    round_data = Round(id=round_id, date=datetime.now(),
                       config=to_yaml(config))
    session.add(round_data)

    m = [MatchResult(
        id=args.id,
        round_id=round_id,
        player_id_0=args.p0,
        player_id_1=args.p1,
        player_name_0=config.players[args.p0].name,
        player_name_1=config.players[args.p1].name,
        status=-1,
        seed=args.seed) for args in matches]
    session.bulk_save_objects(m)
    session.commit()
    return round_id


def update_match_results(results: list[tuple[MatchArgs, str]]):
    n = len(results)
    m = []
    for i in range(n):
        args, json = results[i]
        scores = get_game_scores(json)
        status = 2 if scores[0] == scores[1] else 0 if scores[0] > scores[1] else 1
        data = dict(id=args.id, date=args.date,
                    status=status, result_json=json)
        m += [data]
    session.bulk_update_mappings(MatchResult, m)
    session.commit()


def get_round_list():
    res = session.query(Round).order_by(Round.date.desc()).all()
    return res


def get_match_results_list(round_id: str | None):
    if round_id is None:
        return None
    res = session.query(MatchResult).filter(
        MatchResult.round_id == round_id).order_by(MatchResult.date.desc()).all()
    return res

def get_config_yaml(round_id: str):
    res = session.query(Round.config).filter(Round.id == round_id).all()
    if len(res) == 0:
        return None
    return res[0].config # type: ignore

def get_match_json(match_id: str):
    res = session.query(MatchResult.result_json).filter(MatchResult.id == match_id).all()
    if len(res) == 0:
        return None
    return res[0].result_json # type: ignore


def get_vs_stats_01(round_id: str, p0: int, p1: int) -> list[int]:
    res_01 = session.query(MatchResult.status).filter(MatchResult.round_id == round_id) \
        .filter(MatchResult.player_id_0 == p0).filter(MatchResult.player_id_1 == p1) \
        .all()
    res: list[int] = [0, 0, 0]
    for s in res_01:
        if s.status < 0: # type: ignore
            continue
        res[s.status] += 1 # type: ignore
    return res


def get_vs_stats(round_id: str, p0: int, p1: int) -> list[int]:
    res_a = get_vs_stats_01(round_id, p0, p1)
    res_b = get_vs_stats_01(round_id, p1, p0)
    res_a[0] += res_b[1]
    res_a[1] += res_b[0]
    res_a[2] += res_b[2]
    return res_a
