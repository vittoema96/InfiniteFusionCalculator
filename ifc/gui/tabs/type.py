import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QLabel, QComboBox, QPushButton

from data import utils, pokedex
from data.enums import Type
from data.pokemon import FusedPokemon, Pokemon
from gui.tabs import widgets
from gui.tabs.base import IFCBaseTab


class TypeTab(IFCBaseTab):

    def __init__(self):
        super().__init__()

        self.warn_box = QVBoxLayout()

        # Set label, label with image and combobox for 'based on'
        self.based_on_text = QLabel("BASED ON")
        self.based_on_text.setFont(self.bold_font)
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
            cbox.setFont(self.bold_font)
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
                widgets.URL2LABEL.put(pokemon.get_sprite_url(), self.based_on_image)
                pokemon.fetch_image(self.nam)

            for model in [self.type_a_cbox.model(), self.type_b_cbox.model()]:
                for i in range(len(model.findItems('', flags=Qt.MatchFlag.MatchContains))):
                    model.item(i).setFont(self.font)

        self.based_on_cbox.currentTextChanged.connect(update_pkmn)
        update_pkmn()

        self.sort_by_text = QLabel("SORT BY")
        self.sort_by_text.setFont(self.bold_font)

        self.sort_by_cbox = QComboBox()
        self.sort_by_cbox.setFont(self.font)
        self.sort_by_cbox.addItems([
            "HP", "Attack", "Defence", "Special Attack", "Special Defence", "Speed", "Total"
        ])

        self.search_button = QPushButton("Search")
        self.search_button.setFont(self.bold_font)
        self.search_button.pressed.connect(self.search)

        self.input_layout.addStretch()
        self.input_layout.addLayout(self.warn_box)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.based_on_text)
        self.input_layout.addWidget(self.based_on_image)
        self.input_layout.addWidget(self.based_on_cbox)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.type_a_cbox)
        self.input_layout.addWidget(self.type_b_cbox)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.sort_by_text)
        self.input_layout.addWidget(self.sort_by_cbox)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.search_button)
        self.input_layout.addStretch()

    def search(self):
        self.clear_layout(self.output_layout)

        requested_type_a = Type[self.type_a_cbox.currentText()]
        requested_type_b = Type[self.type_b_cbox.currentText()]
        id_based_on = None
        if self.based_on_cbox.currentText() != '---':
            id_based_on = pokedex.get_id_by_name(self.based_on_cbox.currentText())

        is_based_on = True if id_based_on else False

        result_ab = set()
        result_ba = set()

        type_a_heads = []
        type_a_bodies = []
        if is_based_on:
            based_on = pokedex.get_pokemon(id_based_on)
            if len(based_on.types) > 1:
                if based_on.types[0] == requested_type_a:
                    type_a_heads = [based_on.evoline]
                else:  # based_on.types[1] == requested_type_a
                    type_a_bodies = [based_on.evoline]

            else:
                type_a_heads = [based_on.evoline]
                type_a_bodies = [based_on.evoline]

        else:
            type_a_heads = pokedex.get_evolines_by_type(first_type=requested_type_a)
            type_a_bodies = pokedex.get_evolines_by_type(second_type=requested_type_a)

        type_b_heads = pokedex.get_evolines_by_type(first_type=requested_type_b)
        type_b_bodies = pokedex.get_evolines_by_type(second_type=requested_type_b)

        for evo_head in type_a_heads:
            for evo_body in type_b_bodies:
                result_ab.add((pokedex.get_pokemon(evo_head[0]),
                               pokedex.get_pokemon(evo_body[0])))
        for evo_head in type_b_heads:
            for evo_body in type_a_bodies:
                result_ba.add((pokedex.get_pokemon(evo_head[0]),
                               pokedex.get_pokemon(evo_body[0])))

        for i, (pokemon_1, pokemon_2) in enumerate(result_ab):
            self.add_evoline_widgets(pokemon_1.name,
                                     pokemon_2.name,
                                     display_ba=False)
            logging.info(f"Displayed {i} out of {len(result_ba) + len(result_ab)}")

        for i, (pokemon_1, pokemon_2) in enumerate(result_ba):
            self.add_evoline_widgets(pokemon_1.name,
                                     pokemon_2.name,
                                     display_ab=False)
            logging.info(f"Displayed {i+len(result_ab)} out of {len(result_ba) + len(result_ab)}")