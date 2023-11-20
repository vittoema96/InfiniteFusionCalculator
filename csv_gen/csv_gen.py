import json
import logging
import os.path
import re
from typing import List, Dict, Optional, Any

import pandas as pd
import requests
from requests import RequestException

# todo might want to fix the various 'multiple evotypes' overriding them on ALTERED_EVOS

EVO_DATA = dict()
EVO_DETAIL_MAP = {
    'raticate': 0,
    'sandslash': 0,
    'ninetales': 0,
    'persian': 0,
    'slowbro': 0,
    'slowking': 0,
    'marowak': 0,
    'sylveon': 0,
    'probopass': 1,
    'milotic': 0,
    # overrided evolutions (ALTERED_EVOS)
    'magnezone': 4,
    'leafeon': 4,
    'glaceon': 4
}
AKAS = {
    'aegislash': 'aegislash-shield',
    'giratina': '487',  # 10007
    'mimikyu': '778',  # 10143, 10144, 10145,
    'deoxys': '386',  # 10001, 10002, 10003
}
ALTERED_EVOS = {
    'crobat': [40],
    'politoed': [37, 'king\'s rock'],
    'alakazam': [40, 'linking cord'],
    'machamp': [40, 'linking cord'],
    'golem': [40, 'linking cord'],
    'gengar': [40, 'linking cord'],
    'steelix': [40, 'metal coat'],
    'blissey': [42],
    'scizor': [40, 'metal coat'],
    'electivire': [50, 'electirizer'],
    'magmortar': [50, 'magmarizer'],
    'kingdra': [50, 'dragon scale'],
    'rhyperior': [55, 'protector'],
    'slowking': ['water stone', 'king stone'],
    'magnezone': ['magnet stone'],
    'espeon': ['sun stone'],
    'umbreon': ['moon stone'],
    'leafeon': ['leaf stone'],
    'glaceon': ['ice stone'],
    'sylveon': ['shiny stone'],
    'togetic': [15],
    'pikachu': [15],
    'clefairy': [15],
    'jigglypuff': [15],
    'gliscor': ['dusk stone'],
    'weavile': ['ice stone'],
    'porygon2': ['upgrade'],
    'porygon-z': ['dubious disc'],
    'electabuzz': [25],
    'magmar': [25],
    'marill': [15],
    'wobbuffet': [15],
    'mantine': [21],
    'snorlax': [30],
    'dusknoir': [50],
    'probopass': ['magnet stone'],
    'lucario': [30],
    'milotic': [35],
    'roselia': [15],
    'lopunny': [22]
}


def get_response(url):
    res = requests.get(url)
    if res.status_code != 200:
        logging.error(res)
        raise RequestException(f'Status: {res.status_code}. Message: {res.text}')
    return json.loads(res.text)


def case_capitalize(string: str):
    words = re.split('[ -_]', string)
    return ' '.join([word.capitalize() for word in words])


def parse_abilities(if_idx, abilities: List[Dict]):
    abilities_list = []
    hidden_ability = None

    for ability in abilities:
        ability_name = ability['ability']['name']
        if ability['is_hidden']:
            hidden_ability = ability_name
        else:
            abilities_list.append(ability_name)

    logging.debug(f'Ability A: {case_capitalize(abilities_list[0])}')
    logging.debug(f'Ability B: {case_capitalize(abilities_list[1]) if len(abilities_list)>1 else "None"}')
    df.at[if_idx, 'ABILITIES'] = json.dumps(abilities_list)

    if hidden_ability:
        logging.debug(f'Hidden Ability: {case_capitalize(hidden_ability)}')
        df.at[if_idx, 'HIDDEN'] = hidden_ability


def parse_stats(if_idx, stats: List[Dict]):
    for stat in stats:
        name = stat['stat']['name'].upper()
        value = stat['base_stat']
        logging.debug(f'{name}: {value}')
        df.at[if_idx, name] = int(value)


def parse_types(if_idx, types: List[Dict]):
    types_list = []
    for _type in types:
        name = _type['type']['name'].upper()
        types_list.append(name)

    logging.debug(f'TYPE(s): {types_list}')
    df.at[if_idx, 'TYPES'] = json.dumps(types_list)


def get_levels(link):

    def get_min_level(_link, decrement_level: bool = False):
        evo_details = _link['evolution_details']

        min_level = []
        if evo_details:
            pkmn_name = _link['species']['name']
            if pkmn_name in ALTERED_EVOS.keys():
                min_level = ALTERED_EVOS[pkmn_name]
            else:
                evo_details = evo_details[0 if EVO_DETAIL_MAP.get(pkmn_name) is None else EVO_DETAIL_MAP[pkmn_name]]

                details_keys = list(evo_details.keys())
                if evo_details['trigger']['name'] in ['trade', 'shed']:
                    min_level.append(evo_details['trigger']['name'])
                details_keys.remove('trigger')
                details_keys.remove('time_of_day')

                for level_method_key in details_keys:
                    if evo_details[level_method_key] not in [None, False, '']:
                        level_method_value = evo_details[level_method_key]
                        if level_method_key == 'min_level':
                            level_method_value -= 1 if decrement_level else 0
                        elif level_method_key in ['min_happiness', 'min_beauty',
                                                  'party_species', 'min_affection',
                                                  'relative_physical_stats']:
                            level_method_value = level_method_key
                        elif level_method_key in ['held_item', 'item', 'known_move', 'known_move_type', 'location']:
                            level_method_value = level_method_value.get('name')
                        elif level_method_key == 'gender':
                            level_method_value = 'male' if level_method_value == 2 else 'female'

                        min_level.append(level_method_value)
        else:
            min_level = [1]
        return min_level

    min_level = get_min_level(link)
    max_level = []

    for link in link['evolves_to']:
        try:
            int(df[df['NAME'] == link['species']['name']].index[0])
        except IndexError:
            break  # if evolution species is not present in pokedex don't count it
        max_level.append(get_min_level(link, decrement_level=True))

    if len(max_level) == 1 and isinstance(max_level[0], list):
        max_level = max_level[0]
    if not max_level:
        max_level = [100]

    return min_level, max_level


def parse_evolution(evolves_to: List[Dict[str, Any]],
                    evo_list: Optional[List[int]] = None) -> List[int]:
    if evo_list is None:
        evo_list = []

    for link in evolves_to:
        name = link['species']['name']
        try:
            idx = int(df[df['NAME'] == name].index[0])
        except IndexError:
            break

        evo_list.append(idx)

        min_level, max_level = get_levels(link)
        df.at[idx, 'MIN_LEVEL'] = json.dumps(min_level)
        df.at[idx, 'MAX_LEVEL'] = json.dumps(max_level)

        evo_list = parse_evolution(link['evolves_to'], evo_list)

    return evo_list


def parse_evoline(evoline_url):
    # get evoline unique id
    evo_id = int(evoline_url.split('/')[-2])

    # if evoline was not already parsed, do it and store it
    logging.debug(f'Parsing evoline #{evo_id}')
    if EVO_DATA.get(evo_id) is None:
        evoline = get_response(evoline_url)
        # get the list of ids of evolutions. also sets min/max levels
        evo_list = parse_evolution([evoline['chain']])
        # save evoline
        EVO_DATA[evo_id] = evo_list
        # set evoline to all participants
        for idx in evo_list:
            df.at[idx, 'EVOLINE'] = json.dumps(evo_list)

    else:
        logging.info(f'Evoline #{evo_id} already in storage. Skipping.')


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)

    df = pd.read_csv(os.path.join(os.path.dirname(__file__), 'data_base.csv'),
                     index_col='ID')

    logging.info('Downloading...')
    for i, name in enumerate(df['NAME']):
        i += 1
        logging.info(f'*** [{i}] - {name.upper()} ***')

        result = get_response(f'https://pokeapi.co/api/v2/pokemon/{AKAS.get(name, name)}')
        parse_abilities(i, result['abilities'])
        parse_stats(i, result['stats'])
        parse_types(i, result['types'])
        # todo might want to implement
        moves = result['moves']
        sprites = result['sprites']

        pokemon_species = get_response(f'https://pokeapi.co/api/v2/pokemon-species/{name}')
        parse_evoline(pokemon_species['evolution_chain']['url'])

    swapped_types = [
        'magnemite',
        'magneton',
        'dewgong',
        'omanyte',
        'omastar',
        'scizor',
        'magnezone',
        'empoleon',
        'spiritomb',
        'ferrothorn',
        'celebi'
    ]
    for n in swapped_types:
        row = df[df['NAME'] == n]
        assert row.size == 13
        type_a, type_b = json.loads(row['TYPES'].values[0])
        df.at[row.index[0], 'TYPES'] = json.dumps([type_b, type_a])

    dominant_map = {
        'bulbasaur': 'GRASS', 'ivysaur': 'GRASS', 'venusaur': 'GRASS',
        'charizard': 'FIRE',
        'geodude': 'ROCK', 'graveler': 'ROCK', 'golem': 'ROCK',
        'gastly': 'GHOST', 'haunter': 'GHOST', 'gengar': 'GHOST',
        'onix': 'ROCK',
        'scyther': 'BUG',
        'gyarados': 'WATER',
        'articuno': 'ICE',
        'zapdos': 'ELECTRIC',
        'moltres': 'FIRE',
        'dragonite': 'DRAGON',
        'steelix': 'STEEL'
    }
    for idx in df.index:
        n = df.loc[idx]['NAME']
        if 'NORMAL' in df.loc[idx]['TYPES'] and 'FLYING' in df.loc[idx]['TYPES']:
            df.at[idx, 'TYPES'] = ['FLYING']
        elif n in dominant_map.keys():
            df.at[idx, 'TYPES'] = [dominant_map[n]]
    # todo swapped abilities? (you can always revert fusion)

    for stat in ['HP', 'ATTACK', 'DEFENSE', 'SPECIAL-ATTACK', 'SPECIAL-DEFENSE', 'SPEED']:
        df[stat] = df[stat].astype(dtype=int)
    df.to_csv('data_new.csv')
