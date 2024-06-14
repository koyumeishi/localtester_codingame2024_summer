from datetime import datetime
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor
from serde.yaml import from_yaml
import argparse
from config import Config, Player
from game import run_single_game, get_game_scores
from matchmaker import make_match, MatchArgs
from db import make_new_round, update_match_results, get_vs_stats
from tabulate import tabulate

def process(args: MatchArgs, players: list[Player]) -> tuple[MatchArgs, str]:
    args.date = datetime.now()
    res = run_single_game(args.seed, args.level,
                          players[args.p0], players[args.p1])
    print(datetime.now(), args.seed, args.p0, args.p1, get_game_scores(res))
    return args, res


def process_battles(config: Config):
    n_threads = cpu_count() if config.threads <= 0 else config.threads

    args = make_match(config)

    round_id = make_new_round(config, args)

    with ThreadPoolExecutor(n_threads) as executor:
        # with ProcessPoolExecutor(n_threads) as executor:
        futures = [executor.submit(process, a, config.players)
                   for a in args]
        results: list[tuple[MatchArgs, str]] = []

        save_window_size = 10
        last_saved = 0

        for future in as_completed(futures):
            res = future.result()
            results += [res]
            if len(results) - last_saved >= save_window_size:
                r = results[last_saved:]
                update_match_results(r)
                last_saved = len(results)

    print_vs_stats(config, round_id)
    return results


def print_vs_stats(config: Config, round_id: str):
    n = len(config.players)
    res = [[0 for j in range(n)] for i in range(n)]
    for i in range(n):
        w = [0,0,0]
        for j in range(n):
            if i==j:
                continue
            v = get_vs_stats(round_id, i, j)
            for _ in range(3):
                w[_] += v[_]
            res[i][j] += v[0]
            res[i][i] += v[2]
            print(f'{i} vs {j}')
            headers = ['', 'win', 'lose', 'tie']
            print(tabulate([['cnt'] + v, ['%'] + [100*x/sum(v) for x in v]], headers=headers, floatfmt='.5f'))
            print('')
        
        print(f'{i} vs *')
        headers = ['', 'win', 'lose', 'tie']
        print(tabulate([['cnt'] + w, ['%'] + [100*x/sum(w) for x in w]], headers=headers, floatfmt='.5f'))
        print('')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Path to the configuration YAML file")
    args = parser.parse_args()
    with open(args.config, encoding='utf8') as f:
        yamls = f.read()
        config = from_yaml(Config, yamls)

    res = process_battles(config)
    # print("[" + ",\n\t".join(res) + "]")
