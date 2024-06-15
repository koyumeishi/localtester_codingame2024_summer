import os
import sys
import tempfile
import shutil
from config import Player
import json

# import before importing jnius
cp = list(filter(lambda x: x.lower().endswith('.jar'), os.listdir(os.getcwd())))
os.environ['CLASSPATH'] = cp[-1] if len(cp) > 0 else ""

print(f'CLASSPATH={os.environ["CLASSPATH"]}', file=sys.stderr)
import jnius


class Game:
    def __init__(self, seed: int, level: int, players: list[Player]):
        self.game = jnius.autoclass('com.codingame.gameengine.runner.MultiplayerGameRunner')()
        self.level = level
        self.seed = seed
        self.seed_java = jnius.autoclass('java.lang.Long')(self.seed)
        self.p = players
        self.completed = False

    def simulate(self):
        self.game.setSeed(self.seed_java)
        self.game.setLeagueLevel(self.level)
        for p in self.p:
            self.game.addAgent(p.exec, p.name)
        self.results = self.game.simulate()
        self.completed = True
        return self.results

    def getJSON(self) -> str:
        assert self.completed
        return self.game.getJSONResult()


def run_game(seed: int, level: int, players: list[Player]):
    '''
    run a single game
    returns result json
    '''
    g = Game(seed, level, players)
    g.simulate()
    return g.getJSON()


def generate_assets():
    """
    Writes out the assets required for visualization.
    Executed only on the first run.
    """
    # dummy game
    px = Player("A", 'python -c "print(\'LEFT\' * 200)"', "")
    py = Player("B", 'python -c "print(\'RIGHT\' * 200)"', "")
    pz = Player("C", 'python -c "print(\'UP\' * 200)"', "")

    players = [px, py, pz]
    try:
        game = Game(0, 1, players)
        game.simulate()
        # write assets in tempdir
        Renderer = jnius.autoclass('com.codingame.gameengine.runner.Renderer')
        rend = Renderer(8000) # dummy port
        rend.generateView(game.game.getJSONResult(), None)
    except:
        pass
    # copy into ./visualizer
    source_dir = os.path.join(tempfile.gettempdir(), 'codingame')
    target_dir = os.path.join(os.getcwd(), "visualizer")
    shutil.copytree(source_dir, target_dir, dirs_exist_ok=True)
    print(f'visualizer exported into ./visualizer')


def get_game_scores(jsons: str):
    '''
    getscores for each player of the game
    '''
    scores = json.loads(jsons)['scores']
    return (scores)

def get_game_ranks(jsons: str) -> list[int]:
    '''
    get ranks for each player of the game
    '''
    scores = get_game_scores(jsons)
    ranks = [0, 0, 0]
    for i in range(3):
        for j in range(3):
            if i != j:
                if scores[str(i)] < scores[str(j)]:
                    ranks[i] += 1

    print(ranks)
    return ranks