from glob import glob
import os
from os.path import abspath, basename, dirname, join
from PIL import Image, ImageDraw


path = abspath('./graphs')
out_path = join(path, 'gifs')
os.makedirs(out_path, exist_ok=True)


files = glob(f'{path}/**/merged/*.png', recursive=True)

files_by_game = {}
for fn in files:
    try:
        game_id, play_id, _ = [x for x in dirname(fn).replace(path, '').split(os.path.sep) if x]
    except ValueError:
        continue
    try:
        files_by_game[game_id][play_id].append(fn)
    except KeyError:
        files_by_game[game_id] = {play_id: [fn]}

for k in files_by_game:
    for kk in files_by_game[k]:
        files_by_game[k][kk].sort(key=lambda fn: int(basename(fn).replace('.png', '').split('_')[1]))
        images = [Image.open(fn) for fn in files_by_game[k][kk]]
        out_fn = join(out_path, f'{k}_{kk}.gif')
        images[0].save(out_fn,
                       save_all=True,
                       append_images=images[1:],
                       optimize=False,
                       duration=100,
                       loop=0)

