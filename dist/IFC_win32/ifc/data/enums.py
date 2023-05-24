from enum import Enum


class Type(Enum):
    ANY = '#EAE6CA'
    NORMAL = '#A8A878'
    FIRE = '#F08030'
    WATER = '#6890F0'
    GRASS = '#78C850'
    ELECTRIC = '#F8D030'
    ICE = '#98D8D8'
    FIGHTING = '#C03028'
    POISON = '#A040A0'
    GROUND = '#E0C068'
    FLYING = '#A890F0'
    PSYCHIC = '#F85888'
    BUG = '#A8B820'
    ROCK = '#B8A038'
    GHOST = '#705898'
    DARK = '#705848'
    DRAGON = '#7038F8'
    STEEL = '#B8B8D0'
    FAIRY = '#F0B6BC'

    def __eq__(self, other):
        if self.name == self.ANY.name or (isinstance(other, Type) and other.name == self.ANY.name):
            return True
        return super().__eq__(other)

    def __hash__(self):
        return super.__hash__(self)

    @staticmethod
    def is_any(type_to_check) -> bool:
        """
        Since the __eq__ method was overridden to return True
        to any comparison between ANY and the other Types,
        this is a safe way to check if the Type is actually ANY
        :param type_to_check: The type to check against ANY.
        :return: True if type_to_check is actually the Type ANY.
                 If not, or anything else than a Type is provided, this will return False.
        """
        if isinstance(type_to_check, Type):
            return type_to_check.name == Type.ANY.name
        return False
