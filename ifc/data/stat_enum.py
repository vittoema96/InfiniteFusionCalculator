from enum import Enum

from data.pokemon import AbstractPokemon


class Stat(Enum):

    HP = "HP"
    ATTACK = "ATK"
    DEFENSE = "DEF"
    SPECIAL_ATTACK = "SP.ATK"
    SPECIAL_DEFENSE = "SP.DEF"
    SPEED = "SPEED"
    TOTAL = "TOTAL"

    def get_pretty_name(self):
        if self in [self.TOTAL, self.HP]:
            return self.name.upper()
        else:
            return self.name.replace('_', ' ').title()

    def get_value(self, pokemon: AbstractPokemon):
        return pokemon.__getattribute__(self.name.lower())

    @staticmethod
    def get(name: str):
        name = name.lower()
        for s in Stat:
            if name in [s.name.lower(), s.value.lower(), s.get_pretty_name().lower()]:
                return s
        return None