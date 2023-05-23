from random import Random

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QComboBox

from data import utils, pokedex
from gui.tabs import widgets
from gui.tabs.base import IFCBaseTab


class SingleTab(IFCBaseTab):

    def __init__(self):
        super().__init__()

        # Define the INFO box
        self.info_box = QVBoxLayout()

        info_label = QLabel("<b>INFO</b>")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_message = QLabel("You can see typing and stats of a Pokemon hovering it with the mouse.\n\n"
                              "To keep the application light-weight, "
                              "the sprites are downloaded on every fusion request.")
        info_message.setWordWrap(True)
        info_label.setFont(self.font)
        info_message.setFont(self.font)
        self.info_box.addWidget(info_label)
        self.info_box.addWidget(info_message)

        # Create the 2 inputs for the pokemons (label, combobox and random button)
        self.sprite1, self.cbox1, self.random1 = self.init_input()
        self.sprite2, self.cbox2, self.random2 = self.init_input()

        # Create the FUSE button and connect it to update
        self.fuse_button = QPushButton("Fuse")
        self.fuse_button.setFont(self.bold_font)
        self.fuse_button.pressed.connect(self.update_output)

        # Add everything to input_layout with the correct spaces
        self.input_layout.addStretch()
        self.input_layout.addLayout(self.info_box)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.sprite1)
        self.input_layout.addWidget(self.cbox1)
        self.input_layout.addWidget(self.random1)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.sprite2)
        self.input_layout.addWidget(self.cbox2)
        self.input_layout.addWidget(self.random2)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.fuse_button)
        self.input_layout.addStretch()

    def init_input(self):
        sprite = QLabel()
        sprite.setFixedHeight(utils.SPRITE_SIZE)
        sprite.setFixedWidth(utils.SPRITE_SIZE)
        sprite.setStyleSheet(".QLabel{"
                             "     border: 5px ridge gray;"
                             "}")
        cbox = QComboBox()
        cbox.setFont(self.font)
        cbox.addItems(pokedex.get_names())

        def on_text_changed():
            pokemon = pokedex.get_pokemon(name=cbox.currentText())
            widgets.URL2LABEL.put(pokemon.get_sprite_url(), sprite)
            pokemon.fetch_image(self.nam)

        cbox.currentTextChanged.connect(on_text_changed)
        on_text_changed()

        def get_random():
            items_n = cbox.count()
            idx = Random().randint(0, items_n-1)
            cbox.setCurrentIndex(idx)
        random = QPushButton('Random')
        random.setFont(self.font)
        random.clicked.connect(get_random)
        return sprite, cbox, random

    def update_output(self):
        pkmn1 = self.cbox1.currentText()
        pkmn2 = self.cbox2.currentText()

        self.clear_layout(self.output_layout)

        self.add_evoline_widgets(pkmn1, pkmn2)

