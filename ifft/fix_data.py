import logging

import pandas as pd
import requests
from tqdm import tqdm

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    # load csv with ids and names
    df = pd.read_csv('data.csv', index_col='ID')
    stat_names = ['HP', 'ATK', 'DEF', 'SPATK', 'SPDEF', 'SPD']
    for name in stat_names:
        df[name] = 0
        df[name] = df[name].astype('int')

    for i, name in tqdm(enumerate(df['NAME'])):
        i = i+1
        if name == 'aegislash':
            name = '10026'
        elif name == 'giratina':
            name = '487'
        elif name == 'mimikyu':
            name = '778'
        elif name == 'deoxys':
            name = '386'
        pkmn = requests.get(f"https://pokeapi.co/api/v2/pokemon/{name}").json()

        for k, stat in enumerate(pkmn['stats']):
            df.loc[i, stat_names[k]] = int(stat['base_stat'])


    df