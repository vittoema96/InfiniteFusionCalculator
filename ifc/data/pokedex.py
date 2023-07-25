import json
import os.path
from typing import List

import pandas as pd
from pandas import DataFrame

from data.type_enum import Type
from data.pokemon import Pokemon
from ifc import RESOURCES_PATH

_data: DataFrame = pd.read_csv(os.path.join(RESOURCES_PATH, 'data.csv'), index_col='ID')


def get_names() -> List[str]:
    """
    Returns a list of the names of all the pokemons in the pokedex
    """
    return _data['NAME'].tolist()


def get_types() -> List[str]:
    """
    Returns a list of all available types
    """

    return [t.name for t in [*Type]]


def get_pokemon(idx: int = None, name: str = None) -> Pokemon:
    assert (idx is not None) ^ (name is not None), 'Only one between id or name can be used'

    if idx is None:
        idx = get_id_by_name(name)

    pokemon = Pokemon(_data.loc[idx])

    return pokemon


def get_evolines_by_type(first_type: Type = None, second_type: Type = None) -> List[List[Pokemon]]:
    must_contain = (f'\["{first_type.name}"' if first_type and not Type.is_any(first_type) else "") + \
                   (f', "{second_type.name}"\]' if second_type and not Type.is_any(second_type) else "")
    return [
        get_pokemon(json.loads(evo)[0]).evoline
        for evo in _data[
            _data['TYPES'].str.contains(must_contain)
        ]['EVOLINE'].unique()
    ]



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
