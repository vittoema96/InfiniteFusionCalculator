from __future__ import annotations

import abc
import json
from abc import ABC
from typing import List

import pandas as pd
from PyQt6 import QtNetwork
from PyQt6.QtCore import QUrl
from PyQt6.QtNetwork import QNetworkAccessManager

from data import pokedex
from data.type_enum import Type


class AbstractPokemon(ABC):
    """
    Abstract class.
    Base for utility classed for Pokemon data.
    """

    def __init__(self,
                 name: str,
                 min_level: int, max_level: int,
                 types: List[Type],
                 hp: int,
                 attack: int, defense: int,
                 spatk: int, spdef: int,
                 speed: int):

        self._name = name

        self._min_level = min_level
        self._max_level = max_level

        self._types = types

        self._hp = hp
        self._atk = attack
        self._def = defense
        self._spatk = spatk
        self._spdef = spdef
        self._spd = speed

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
    def types(self) -> List[Type]:
        return self._types

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def attack(self) -> int:
        return self._atk

    @property
    def defense(self) -> int:
        return self._def

    @property
    def special_attack(self) -> int:
        return self._spatk

    @property
    def special_defense(self) -> int:
        return self._spdef

    @property
    def speed(self) -> int:
        return self._spd

    @property
    def total(self) -> int:
        return self.hp + self.attack + self.defense + self.special_attack + self.special_defense + self.speed

    def fetch_image(self, nam: QNetworkAccessManager) -> None:
        qurl = QtNetwork.QNetworkRequest(QUrl(self.get_sprite_url()))
        nam.get(qurl)

    @abc.abstractmethod
    def get_sprite_url(self) -> str:
        raise NotImplementedError("Implement this method!")


class Pokemon(AbstractPokemon):
    """
    Utility class for (unfused) Pokemon data.
    Used to access csv data in an easier way.
    """

    def __init__(self, series: pd.Series):
        assert len(series.index) == 11, f'Not enough values in Series {series}'
        for i in range(4):
            assert series.index[i] in ['NAME',
                                       'MIN_LEVEL', 'MAX_LEVEL',
                                       'EVOLINE',
                                       'TYPES',
                                       'HP', 'ATK', 'DEF', 'SPATK', 'SPDEF', 'SPD'], \
                f"{series.index[i]} is not a valid index"

        self._evoline = json.loads(series['EVOLINE'])

        super().__init__(name=series['NAME'],
                         min_level=series['MIN_LEVEL'], max_level=series['MAX_LEVEL'],
                         types=[Type[t] for t in json.loads(series['TYPES'])],
                         hp=series['HP'],
                         attack=series['ATK'], defense=series['DEF'],
                         spatk=series['SPATK'], spdef=series['SPDEF'],
                         speed=series['SPD'])

    @property
    def evoline(self) -> List[Pokemon]:
        """
        List containing the IDs of all the Pokemon in this evolution line.
        """
        return [pokedex.get_pokemon(idx) for idx in self._evoline]

    @property
    def raw_evoline(self) -> List[int]:
        """
        List containing the IDs of all the Pokemon in this evolution line.
        """
        return self._evoline

    def get_sprite_url(self) -> str:
        return f"https://img.pokemondb.net/sprites/black-white/normal/{self.name}.png"


class FusedPokemon(AbstractPokemon):
    """
    Utility class for Fused Pokemon data.
    Calculates typing and stats given a head and body pokemon.
    """

    def __init__(self, head: Pokemon, body: Pokemon):
        super().__init__(name=head.name+"/"+body.name,
                         min_level=max(head.min_level, body.min_level),
                         max_level=min(head.max_level, body.max_level),
                         types=[head.types[0],
                                body.types[1]
                                if len(body.types) > 1 and body.types[1] != head.types[0]
                                else body.types[0]],
                         hp=int((body.hp + head.hp*2)/3),
                         attack=int((body.attack*2 + head.attack)/3),
                         defense=int((body.defense * 2 + head.defense) / 3),
                         spatk=int((body.special_attack + head.special_attack * 2) / 3),
                         spdef=int((body.special_defense + head.special_defense * 2) / 3),
                         speed=int((body.speed*2 + head.speed)/3))
        self._head = head.name
        self._body = body.name

    @property
    def head(self):
        return self._head

    @property
    def body(self):
        return self._body

    def get_sprite_url(self):
        from data import pokedex
        head_id = pokedex.get_id_by_name(self.head)
        body_id = pokedex.get_id_by_name(self.body)
        return f"https://raw.githubusercontent.com/Aegide/custom-fusion-sprites/" \
               f"main/CustomBattlers/{head_id}.{body_id}.png"
