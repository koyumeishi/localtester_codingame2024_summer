from datetime import datetime
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from serde.yaml import from_yaml
import argparse
from config import Config, Player
from game import run_game, get_game_scores
from matchmaker import make_match, BattleConfig
import db

def run_single_battle(args: BattleConfig, players: list[Player]) -> tuple[BattleConfig, str]:
    '''
    process single battle
    returns (config, result_json)
    '''
    args.date = datetime.now()
    res = run_game(args.seed, args.level,
                          players)
    print(datetime.now(), args.seed, args.p0, args.p1, args.p2, get_game_scores(res))
    return args, res


def process_all_battles(config: Config):
    '''
    process all battles of the round
    '''
    n_threads = cpu_count() if config.threads <= 0 else config.threads

    # make battle list
    args: list[BattleConfig] = make_match(config)

    # prepare database
    round_id: str = db.make_new_round(config, args)

    with ThreadPoolExecutor(n_threads) as executor:
    # with ProcessPoolExecutor(n_threads) as executor:
        futures = [executor.submit(run_single_battle, a, config.players)
                   for a in args]
        results: list[tuple[BattleConfig, str]] = []

        # sava_window_size 貯まる毎に database を更新
        save_window_size = 10
        last_saved = 0

        for future in as_completed(futures):
            res = future.result()
            results += [res]
            if len(results) - last_saved >= save_window_size:
                r = results[last_saved:]
                db.update_match_results(r)
                last_saved = len(results)
        
        if last_saved < len(results):
            r = results[last_saved:]
            db.update_match_results(r)

    return results


        
def main():
    '''
    run battles
    `python3 runner.py config.yaml`
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Path to the configuration YAML file")
    args = parser.parse_args()
    with open(args.config, encoding='utf8') as f:
        yamls = f.read()
        config = from_yaml(Config, yamls)

    res = process_all_battles(config)
    # print("[" + ",\n\t".join(res) + "]")

if __name__ == "__main__":
    main()
