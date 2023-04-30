import json
from typing import List, Dict, Union, Tuple

import pandas as pd
from pandas import DataFrame

from data.pokemon import Pokemon

_data: DataFrame = pd.read_csv('data.csv', index_col='ID')


def get_names() -> List[str]:
    """
    Returns a list of the names of all the pokemons in the pokedex
    """
    return _data['NAME'].tolist()


def get_pokemon(idx: int = None, name: str = None) -> Pokemon:
    assert (idx is not None) ^ (name is not None), 'Only one between id or name can be used'
    if idx is not None:
        return Pokemon(_data.loc[idx])
    return Pokemon(_data[get_id_by_name(name)])


def get_id_by_name(name: str) -> int:
    """
    Returns the ID of the pokemon with name 'name'
    :param name: The name of the pokemon to get the id of
    :return: The id of the pokemon
    """
    return int(_data[_data['NAME'] == name].index[0])


def get_evolution_list(name: str) -> List[Pokemon]:
    result = list()

    for idx in json.loads(_data.loc[get_id_by_name(name)]['EVOLINE']):
        result.append(get_pokemon(idx=idx))
    result.sort(key=lambda a: a.min_level)
    return result
