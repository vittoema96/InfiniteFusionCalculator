import json
import logging
import os.path

import pandas as pd
import requests
from tqdm import tqdm

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # load csv with ids and names
    df = pd.read_csv('data_new.csv', index_col='ID')
    df['MIN_LEVEL'] = -999
    df['MAX_LEVEL'] = -999
    df['EVOLINE'] = -999

    df['EVOLINE'] = df['EVOLINE'].astype('object')

    chain_urls = set()

    if os.path.isfile('urls.txt'):
        logging.info('urls.txt file found, loading urls from it')
        with open('urls.txt') as file:
            chain_urls = [url.replace('\n', '') for url in file.readlines()]
    else:
        logging.info('No urls.txt file found, downloading urls')
        for name in tqdm(df['NAME']):
            species = requests.get(f"https://pokeapi.co/api/v2/pokemon-species/{name}").json()
            chain_urls.add(species['evolution_chain']['url'])

        with open('urls.txt', 'w') as file:
            logging.info('Saving urls to urls.txt file')
            file.writelines([url+'\n' for url in chain_urls])

    def get_max_level(chain):
        if len(chain['evolves_to']) > 0:
            max_level = 0
            for evolution in chain['evolves_to']:
                val = evolution['evolution_details'][0]['min_level']
                max_level = max_level if val is None or max_level > val else val
            return max_level - 1 if max_level and max_level != 0 else 100
        return 100

    for url in tqdm(chain_urls):
        chain = requests.get(url).json()['chain']
        evo = []

        name = chain['species']['name']
        min_level = 0
        last_min_level = 0
        max_level = get_max_level(chain)

        idx = df[df['NAME'] == name].index[0]
        evo.append(int(idx))
        df.loc[idx, 'MIN_LEVEL'] = min_level
        df.loc[idx, 'MAX_LEVEL'] = max_level

        while len(chain['evolves_to']) > 0:
            for chain in chain['evolves_to']:
                name = chain['species']['name']
                if name not in df['NAME'].values:
                    logging.info(f'"{name}" is not a Pokemon present in the game, skipping it')
                    continue
                val = chain['evolution_details'][0]['min_level']
                min_level = val
                min_level = min_level if min_level else last_min_level
                last_min_level = min_level
                max_level = get_max_level(chain)

                try:
                    idx = df[df['NAME'] == name].index[0]
                    evo.append(int(idx))
                    df.loc[idx, 'MIN_LEVEL'] = min_level
                    df.loc[idx, 'MAX_LEVEL'] = max_level
                except IndexError as e:
                    logging.warning(f"(SHOULD NOT HAPPEN) Pokemon '{name}' could not be found in InfiniteFusion dex, skipping it")

        for idx in evo:
            df.loc[idx, 'EVOLINE'] = json.dumps(evo)
    df.to_csv('data.csv')