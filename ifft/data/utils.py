from typing import Tuple, List

from data.pokedex import get_evolution_list, get_id_by_name
from data.pokemon import Pokemon

""" Short name for the app"""
SHORTNAME: str = "IFFT"
""" Name of the app"""
NAME: str = "Infinite Fusion Family Tree"
""" Version of the app """
VERSION: str = "0.2"

""" The size that a Pokémon Sprite must have (1:1 ratio) """
SPRITE_SIZE: int = 100
""" Margin to use in the app """
MARGIN: int = 10

TITLE: str = SHORTNAME + ' - ' + NAME + ' v' + VERSION


def get_fusion_urls(name1: str, name2: str) -> \
        Tuple[
            List[Tuple[Pokemon, Pokemon, str]],
            List[Tuple[Pokemon, Pokemon, str]]
        ]:
    """
    Returns 2 lists containing 2 pokemon and an url
    List 1 has fusions with head <pokemon from evoline of pkmn1>
    and body <pokemon from evoline of pkmn2>,
    List 2 has fusions with head <pokemon from evoline of pkmn2>
    and body <pokemon from evoline of pkmn1>
    """
    l1 = get_evolution_list(name1)
    l2 = get_evolution_list(name2)

    result_ab = []
    result_ba = []
    for i, a in enumerate(l1):
        for b in l2:
            if min(a.max_level, b.max_level) - max(a.min_level, b.min_level) >= 0:
                aid = get_id_by_name(a.name)
                bid = get_id_by_name(b.name)
                result_ab.append((
                        a, b,
                        get_fusion_sprite_url(aid, bid)
                ))
                if a.name != b.name:
                    result_ba.append((
                            b, a,
                            get_fusion_sprite_url(bid, aid)
                    ))

    return result_ab, result_ba


def get_sprite_url(name: str) -> str:
    """
    Returns the url for a sprite of a non-fusion pokemon
    :param name: The name of the Pokemon to get the sprite of
    :return: The url to the sprite
    """
    return f"https://img.pokemondb.net/sprites/black-white/normal/{name}.png"


def get_fusion_sprite_url(id_a: int, id_b: int):
    """
    Returns the url for a sprite of a fusion pokemon (order of arguments matter)
    :param id_a: The id of the head Pokemon
    :param id_b: The id of the body Pokemon
    :return: The url to the fusion sprite
    """
    return f"https://raw.githubusercontent.com/Aegide/custom-fusion-sprites/main/CustomBattlers/{id_a}.{id_b}.png"



