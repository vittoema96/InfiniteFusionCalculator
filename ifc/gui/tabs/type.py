import logging
from random import Random

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QComboBox

from data import utils, pokedex
from data.stat_enum import Stat
from data.type_enum import Type
from gui.tabs.base import IFCBaseTab
from gui.tabs.widgets import FuseButtonsWidget
from gui.widget_painter import WidgetPainter


class TypeTab(IFCBaseTab):

    def __init__(self):
        super().__init__()

        self.set_warning_message("Be aware that this mode may potentially have to load "
                                 "hundreds of evolines at once, so be patient after clicking "
                                 "the 'SEARCH' button")
        # Set label, label with image and combobox for 'based on'
        self.based_on_text = QLabel("BASED ON")
        self.based_on_text.setFont(utils.get_font(bold=True))
        self.based_on_image = QLabel()
        self.based_on_image.setFixedHeight(utils.SPRITE_SIZE)
        self.based_on_image.setFixedWidth(utils.SPRITE_SIZE)
        self.based_on_image.setStyleSheet("QLabel{"
                                          "     border: 5px ridge gray;"
                                          "}")
        self.based_on_cbox = QComboBox()
        self.based_on_cbox.addItems(['---'] + pokedex.get_names())

        def get_type_cbox():
            cbox = QComboBox()
            cbox.setFont(utils.get_font(bold=True))
            cbox.currentTextChanged.connect(
                lambda:
                cbox.setStyleSheet(
                    ".QComboBox{"
                    f" background-color: "
                    f" {Type[cbox.currentText()].value if cbox.currentText() in pokedex.get_types() else 'gray'};"
                    "  color: white;"
                    "  border-radius: 7px;"
                    "  padding: 8px;"
                    "}")
            )
            return cbox

        self.type_a_cbox = get_type_cbox()

        self.type_b_cbox = get_type_cbox()

        def update_pkmn():
            self.type_a_cbox.clear()
            self.type_b_cbox.clear()

            if self.based_on_cbox.currentText() == '---':
                types_no_any = pokedex.get_types()
                types_no_any.remove('ANY')
                self.type_a_cbox.addItems(types_no_any)
                self.type_b_cbox.addItems(types_no_any)
                self.based_on_image.clear()
            else:
                pokemon = pokedex.get_pokemon(name=self.based_on_cbox.currentText())
                self.type_a_cbox.addItems([t.name for t in pokemon.types])
                self.type_b_cbox.addItems(pokedex.get_types())
                self.type_b_cbox.setCurrentText('ANY')
                WidgetPainter().put(pokemon.get_sprite_url(), self.based_on_image)

            for model in [self.type_a_cbox.model(), self.type_b_cbox.model()]:
                for i in range(len(model.findItems('', flags=Qt.MatchFlag.MatchContains))):
                    model.item(i).setFont(utils.get_font())

        self.based_on_cbox.currentTextChanged.connect(update_pkmn)
        update_pkmn()

        self.sort_by_text = QLabel("SORT BY")
        self.sort_by_text.setFont(utils.get_font(bold=True))

        # Create the FUSE button and connect it to update
        self.fuse_buttons_widget = FuseButtonsWidget(self.update_output)

        self.input_layout.addStretch()
        self.input_layout.addWidget(self.based_on_text)
        self.input_layout.addWidget(self.based_on_image)
        self.input_layout.addWidget(self.based_on_cbox)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.type_a_cbox)
        self.input_layout.addWidget(self.type_b_cbox)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.fuse_buttons_widget)
        self.input_layout.addStretch()

    def _get_input_info(self, random: bool = False):
        if random:
            r = Random()
            if r.randint(1, 3) > 1:
                self.based_on_cbox.setCurrentText(r.choice(pokedex.get_names()).lower())
            else:
                self.based_on_cbox.setCurrentText('---')
            self.type_a_cbox.setCurrentIndex(r.randint(0, self.type_a_cbox.count()-1))
            self.type_b_cbox.setCurrentIndex(r.randint(0, self.type_b_cbox.count()-1))

        pokemon = None if self.based_on_cbox.currentText() == '---' \
            else pokedex.get_pokemon(name=self.based_on_cbox.currentText())

        return pokemon, Type[self.type_a_cbox.currentText()], Type[self.type_b_cbox.currentText()]

    def update_output(self, order: Stat, random: bool = False):
        self.clear_layout(self.output_layout)

        based_on, requested_type_a, requested_type_b = self._get_input_info(random=random)

        type_a_heads = list()
        type_a_bodies = list()
        if based_on:
            for evo in based_on.evoline:
                if evo.types[0] == requested_type_a:
                    type_a_heads = [based_on.evoline]
                # Add either if there is a single type or there are 2 and the second matches
                if bool(len(evo.types) > 2) == bool(evo.types[len(evo.types)-1] == requested_type_a):
                    type_a_bodies = [based_on.evoline]

        else:
            type_a_heads = pokedex.get_evolines_by_type(first_type=requested_type_a)
            type_a_bodies = pokedex.get_evolines_by_type(second_type=requested_type_a)

        type_b_heads = pokedex.get_evolines_by_type(first_type=requested_type_b)
        type_b_bodies = pokedex.get_evolines_by_type(second_type=requested_type_b)

        def get_list(heads, bodies, type_a, type_b):
            result = set()
            for evo_head in heads:
                for evo_body in bodies:
                    fusions = utils.get_fusions(evo_head, evo_body)
                    for fusion in fusions[0]:
                        if type_a in fusion.types and type_b in fusion.types:
                            attr = order.name.lower()
                            result.add(
                                (
                                    max([f.__getattribute__(attr)
                                         if type_a in f.types and type_b in f.types
                                         else 0
                                         for f in fusions[0]]),
                                    evo_head[0],
                                    evo_body[0]
                                )
                            )
                            break
            return list(result)

        result_ab = get_list(type_a_heads, type_b_bodies, requested_type_a, requested_type_b)
        result_ba = get_list(type_b_heads, type_a_bodies, requested_type_a, requested_type_b)
        result = result_ba + result_ab

        if based_on and Type.is_any(requested_type_b):
            result_ab2 = get_list([based_on.evoline],
                                  pokedex.get_evolines_by_type(second_type=requested_type_a),
                                  requested_type_a, requested_type_b)
            result_ba2 = get_list(type_a_heads,
                                  [based_on.evoline],
                                  requested_type_a, requested_type_b)
            result += result_ab2 + result_ba2

        result.sort(reverse=True, key=lambda v: v[0])

        for i, (val, pokemon_1, pokemon_2) in enumerate(result):
            self.add_evoline_widgets(pokemon_1,
                                     pokemon_2,
                                     display_ba=False)
            logging.info(f"Displayed {i+1} out of {len(result)}")
