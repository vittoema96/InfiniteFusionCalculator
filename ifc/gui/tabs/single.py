from random import Random

from PyQt6.QtWidgets import QLabel, QPushButton, QComboBox

from data import utils, pokedex
from data.stat_enum import Stat
from gui.tabs.base import IFCBaseTab
from gui.tabs.widgets import FuseButtonsWidget
from gui.widget_painter import WidgetPainter


class SingleTab(IFCBaseTab):

    def __init__(self):
        super().__init__()

        # Create the 2 inputs for the pokemons (label, combobox and random button)
        self.sprite1, self.cbox1, self.random1 = self.init_input()
        self.sprite2, self.cbox2, self.random2 = self.init_input()

        # Create the FUSE button and connect it to update
        self.fuse_buttons_widget = FuseButtonsWidget(self.update_output)

        # Add everything to input_layout with the correct spaces

        self.set_info_message("You can see typing and stats of a Pokemon hovering it with the mouse.\n\n"
                              "Right click on a fusion to select it, hovering over other fusions will show "
                              "stat comparison.")
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.sprite1)
        self.input_layout.addWidget(self.cbox1)
        self.input_layout.addWidget(self.random1)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.sprite2)
        self.input_layout.addWidget(self.cbox2)
        self.input_layout.addWidget(self.random2)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.fuse_buttons_widget)
        self.input_layout.addStretch()

    @staticmethod
    def init_input():
        sprite = QLabel()
        sprite.setFixedHeight(utils.SPRITE_SIZE)
        sprite.setFixedWidth(utils.SPRITE_SIZE)
        sprite.setStyleSheet(".QLabel{"
                             "     border: 5px ridge gray;"
                             "}")
        cbox = QComboBox()
        cbox.setFont(utils.get_font())
        cbox.addItems(pokedex.get_names())

        def on_text_changed():
            pokemon = pokedex.get_pokemon(name=cbox.currentText())
            WidgetPainter().put(pokemon.get_sprite_url(), sprite)

        cbox.currentTextChanged.connect(on_text_changed)
        on_text_changed()

        def get_random():
            items_n = cbox.count()
            idx = Random().randint(0, items_n-1)
            cbox.setCurrentIndex(idx)
        random = QPushButton('Random')
        random.setFont(utils.get_font())
        random.clicked.connect(get_random)
        return sprite, cbox, random

    def update_output(self, order: Stat, random: bool = False):
        if random:
            self.random1.click()
            self.random2.click()
        pkmn1 = pokedex .get_pokemon(name=self.cbox1.currentText())
        pkmn2 = pokedex .get_pokemon(name=self.cbox2.currentText())

        self.clear_layout(self.output_layout)

        self.add_fusions(fusions=[(pkmn1, pkmn2)], order=order)
