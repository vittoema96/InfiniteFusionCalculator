import json
from typing import List

import pandas as pd

from data.enums import Type


class Pokemon:

    _name: str
    _min_level: int
    _max_level: int
    _evoline: List[int]
    _types: List[Type]

    _hp: int
    _atk: int
    _def: int
    _spatk: int
    _spdef: int
    _spd: int

    def __init__(self, series: pd.Series):
        assert len(series.index) == 11, f'Not enough values in Series {series}'
        for i in range(4):
            assert series.index[i] in ['NAME',
                                       'MIN_LEVEL', 'MAX_LEVEL',
                                       'EVOLINE',
                                       'TYPES',
                                       'HP', 'ATK', 'DEF', 'SPATK', 'SPDEF', 'SPD'], \
                f"{series.index[i]} is not a valid index"

        self._name = series['NAME']
        self._min_level = series['MIN_LEVEL']
        self._max_level = series['MAX_LEVEL']
        self._evoline = json.loads(series['EVOLINE'])
        types = json.loads(series['TYPES'])
        self._types = [Type[t] for t in types]
        self._hp = series['HP']
        self._atk = series['ATK']
        self._def = series['DEF']
        self._spatk = series['SPATK']
        self._spdef = series['SPDEF']
        self._spd = series['SPD']

    @property
    def name(self) -> str:
        return self._name

    @property
    def min_level(self) -> int:
        return self._min_level

    @property
    def max_level(self) -> int:
        return self._max_level

    @property
    def evoline(self) -> List[int]:
        return self._evoline

    @property
    def types(self) -> List[Type]:
        return self._types

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def attack(self) -> int:
        return self._atk

    @property
    def defence(self) -> int:
        return self._def

    @property
    def spatk(self) -> int:
        return self._spatk

    @property
    def spdef(self) -> int:
        return self._spdef

    @property
    def speed(self) -> int:
        return self._spd

