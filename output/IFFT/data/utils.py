import json

import pandas as pd
from pandas import DataFrame


_data: DataFrame = pd.read_csv('data.csv', index_col='ID')
_names = _data['NAME'].tolist()


def get_pokemon_names():
    return _names


def get_id_by_name(name: str):
    return int(_data[_data['NAME'] == name].index[0])


def get_vanilla_sprite_url(name: str):
    return f"https://img.pokemondb.net/sprites/black-white/normal/{name}.png"


def get_fusion_sprite_url(id_a: int, id_b: int):
    return f"https://raw.githubusercontent.com/Aegide/custom-fusion-sprites/main/CustomBattlers/{id_a}.{id_b}.png"


def get_fusion_urls(name1: str, name2: str):
    l1 = get_evolution_list(name1)
    l2 = get_evolution_list(name2)

    resultAB = []
    resultBA = []
    for i, a in enumerate(l1):
        for b in l2:
            if min(a['maxLevel'], b['maxLevel']) - max(a['minLevel'], b['minLevel']) > 0:
                aid = get_id_by_name(a['name'])
                bid = get_id_by_name(b['name'])
                print(f'[{a["name"]}]x[{b["name"]}] {max(a["minLevel"], b["minLevel"])}-{min(a["maxLevel"], b["maxLevel"])}')
                resultAB.append(
                    (
                        [
                            a["name"].capitalize(),
                            b["name"].capitalize(),
                            max(a["minLevel"], b["minLevel"]),
                            min(a["maxLevel"], b["maxLevel"])
                        ],
                        get_fusion_sprite_url(aid, bid)
                    )
                )
                resultBA.append(
                    (
                        [
                            b["name"].capitalize(),
                            a["name"].capitalize(),
                            max(a["minLevel"], b["minLevel"]),
                            min(a["maxLevel"], b["maxLevel"])
                        ],
                        get_fusion_sprite_url(bid, aid)
                    )
                )

    return resultAB, resultBA


def get_evolution_list(name: str):
    result = list()

    for idx in json.loads(_data[_data['NAME'] == name]['EVOLINE'].values[0]):
        d = _data.loc[idx]
        result.append({
            'name': d['NAME'],
            'minLevel': int(d['MIN_LEVEL']),
            'maxLevel': int(d['MAX_LEVEL'])
        })
    result.sort(key=lambda a: a['minLevel'])
    return result
