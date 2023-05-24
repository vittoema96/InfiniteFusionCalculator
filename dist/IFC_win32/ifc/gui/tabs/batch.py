from itertools import combinations
from random import Random

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QPushButton, QListWidget

from data import pokedex
from gui.tabs.base import IFCBaseTab


class BatchTab(IFCBaseTab):

    def __init__(self):
        super().__init__()

        self.set_info_message("Add multiple Pokemon to the list and see all "
                              "the possible combinations between them!")

        self.cbox = QComboBox()
        self.cbox.setFont(self.font)
        self.cbox.addItems(pokedex.get_names())

        self.add = QPushButton("Add")
        self.add.setFont(self.font)
        self.plist = QListWidget()
        self.plist.setFont(self.font)
        self.add.pressed.connect(self.update_list)

        self.random = QPushButton("Add Random")
        self.random.setFont(self.font)

        def get_random():
            items_n = self.cbox.count()
            idx = Random().randint(0, items_n-1)
            self.cbox.setCurrentIndex(idx)
            self.update_list()

        self.random.clicked.connect(get_random)

        self.remove = QPushButton("Remove")
        self.remove.setFont(self.font)
        self.remove.pressed.connect(self.remove_from_list)

        self.fuse = QPushButton("Cross Fuse")
        self.fuse.setFont(self.bold_font)
        self.fuse.pressed.connect(self.mix)

        self.input_layout.addStretch()
        self.input_layout.addWidget(self.cbox)
        self.input_layout.addWidget(self.add)
        self.input_layout.addWidget(self.random)
        self.input_layout.addWidget(self.remove)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.plist)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.fuse)
        self.input_layout.addStretch()

    def remove_from_list(self) -> None:
        indexes_to_remove = [item.row() for item in self.plist.selectedIndexes()]
        for index in indexes_to_remove:
            item = self.plist.takeItem(index).text()
            if self.cbox.findText(item, Qt.MatchFlag.MatchExactly) == -1:
                for evo in pokedex.get_evolution_list(item):
                    self.cbox.addItem(evo.name)

    def update_list(self) -> None:
        """
        Adds the Pokemon selected in the cbox to the list.
        If the Pokemon (ar any of its evolutionary line) are already present,
        add them and remove them from the cbox list
        """
        item_to_add = self.cbox.currentText()
        evo_list = [evo.name for evo in pokedex.get_evolution_list(item_to_add)]

        # check if any evolution is already in the list
        for evo in evo_list:
            if self.plist.findItems(evo, Qt.MatchFlag.MatchExactly):
                # if it is, remove all of them from the list, then break the cycle
                for e in evo_list:
                    self.cbox.removeItem(self.cbox.findText(e))
                break
        self.plist.addItem(item_to_add)

    def mix(self):
        self.clear_layout(self.output_layout)

        result = []
        for i in range(self.plist.count()):
            result.append(self.plist.item(i).text())

        # extract duplicates and set result to contain unique elements
        duplicates = set([name for name in result if result.count(name) > 1])
        result = list(set(result))

        # get a list of all combinations of 2 pokemons
        result = list(combinations(result, 2))

        # if there were duplicates, add them to the list
        for duplicate in duplicates:
            result.append((duplicate, duplicate))

        for i, (pkmn1, pkmn2) in enumerate(result):
            self.add_evoline_widgets(pkmn1, pkmn2)
            print(i+1, '/', len(result))
