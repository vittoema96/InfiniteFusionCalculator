import os
from typing import Tuple, List, Optional

from PyQt6.QtGui import QFontDatabase, QFont

from data.pokedex import get_evolution_list
from data.pokemon import FusedPokemon
from ifc import FONTS_PATH

""" Short name for the app"""
SHORTNAME: str = "IFC"
""" Name of the app"""
NAME: str = "InfiniteFusionCalculator by vittoema96"

MAJOR: int = 0
MINOR: int = 3
PATCH: int = 0

""" Version of the app (in string form) """
VERSION: str = f"{MAJOR}.{MINOR}" + (f"{PATCH}" if PATCH > 0 else "")

""" The size that a Pokémon Sprite must have (1:1 ratio) """
SPRITE_SIZE: int = 100
""" Margin to use in the app """
MARGIN: int = 10

TITLE: str = SHORTNAME + ' - ' + NAME + ' v' + VERSION


def get_font(font_size: int = 12,
             bold: bool = False,
             italic: bool = False,
             underline: bool = False) -> QFont:
    font_id = QFontDatabase.addApplicationFont(os.path.join(FONTS_PATH, "pokemon_pixel_font.ttf"))
    assert font_id >= 0, 'Could not find font'
    font_name = QFontDatabase.applicationFontFamilies(font_id)[0]

    qfont = QFont(font_name, font_size)
    qfont.setBold(bold)
    qfont.setItalic(italic)
    qfont.setUnderline(underline)
    return qfont


def get_fusions(name1: str, name2: str) -> \
        Tuple[
            List[FusedPokemon],
            List[FusedPokemon]
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
            fusion_ab = FusedPokemon(a, b)
            fusion_ba = FusedPokemon(b, a)
            if fusion_ab.max_level - fusion_ba.min_level >= 0:
                result_ab.append(fusion_ab)
                if a.name != b.name:
                    result_ba.append(fusion_ba)

    return result_ab, result_ba
