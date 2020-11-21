from glob import glob
import json
from os.path import basename
import pandas as pd


path = './graphs/gifs'

df = pd.read_csv('plays.csv')

files = glob(path + '/*.gif')
for fn in files:
    game_id, play_id = basename(fn).replace('.gif', '').split('_')
    game_id = int(game_id)
    play_id = int(play_id)
    row = df.loc[(df['gameId'] == game_id) & (df['playId'] == play_id)].to_dict()
    meta_fn = fn.replace('.gif', '.meta')
    with open(meta_fn, 'w') as f:
        json.dump(row, f, indent=2)

