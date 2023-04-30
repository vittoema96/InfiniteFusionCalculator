from itertools import combinations
from typing import Optional

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFontDatabase, QFont, QPalette
from PyQt6.QtWidgets import QComboBox, QVBoxLayout, QPushButton, QListWidget, QLabel, QWidget, QHBoxLayout, QTabWidget, \
    QGridLayout, QScrollArea

from ifft.data import utils


class IFFTTabs(QTabWidget):

    def __init__(self, image_size: int, margin: int):
        super().__init__()
        # init size values

        self.addTab(_SingleTab(image_size, margin), "Single")
        self.addTab(_BatchTab(image_size, margin), "Batch")


class _IFFTBaseTab(QWidget):

    """ The size that a Pokémon Sprite must have (1:1 ratio) """
    SPRITE_SIZE: int
    """ Distance between two sprites """
    MARGIN: int

    def __init__(self, image_size: int, margin: int):
        super().__init__()
        self.SPRITE_SIZE = image_size
        self.MARGIN = margin

        self.panel = QHBoxLayout()
        self.panel.setAlignment(Qt.AlignmentFlag.AlignLeading)
        self.setLayout(self.panel)

        w = QWidget()
        self.input = QVBoxLayout()
        w.setLayout(self.input)
        w.setFixedWidth(2 * self.MARGIN + self.SPRITE_SIZE)

        self.panel.addWidget(w)

        scroll = QScrollArea()
        w2 = QWidget()
        self.fusion_space = QVBoxLayout()
        w2.setLayout(self.fusion_space)
        w2.setFixedWidth(10 * self.SPRITE_SIZE)
        scroll.setWidget(w2)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        self.panel.addWidget(scroll)

    def update(self):
        raise NotImplementedError()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clear_layout(child.layout())

    def set_pixmap_from_url(self, label: QLabel, url: str, height: Optional[int] = None):
        response = requests.get(url)
        pixmap = QPixmap()
        n = url.split("/")[-1].split('.')[0]

        if response.status_code == 404:
            response = requests.get(url.replace("main/CustomBattlers", "master/Battlers"))
        if response.status_code == 404:
            response = requests.get(url.replace("main/CustomBattlers", f"master/Battlers/{n}"))
        if response.status_code == 404:
            response = requests.get(url.replace("main/CustomBattlers", f"master/Battlers/{n}").replace("custom", "autogen"))

        pixmap.loadFromData(response.content)

        if height:
            pixmap = pixmap.scaledToHeight(height)

        label.setPixmap(pixmap)

    def get_info_box(self, name1: str, name2: str, min_level: int, max_level: int):
        """
        Creates a Vertical layout displaying the name of the 2 fused Pokemons,
        including which part is which, and min-max level of that particular evo
        :param name1: name of the "head" pokemon
        :param name2: name of the "torso" pokemon
        :param min_level: min level of this particular evolution
        :param max_level: max level of this particular evolution
        :return:a QVBoxLayout containing the labels formatted
        """
        # init custom font
        id = QFontDatabase.addApplicationFont("pokemon_pixel_font.ttf")
        assert id >= 0, 'Could not find font'
        families = QFontDatabase.applicationFontFamilies(id)

        result = QWidget()
        # Set background style of info widget
        result.setStyleSheet(".QWidget{ "
                             f" width: {int(self.SPRITE_SIZE/2)};"
                             f" height: {self.SPRITE_SIZE};"
                             "  border-radius: 15px; "
                             "  border-bottom-left-radius: 3px;"
                             "  background: qlineargradient( x1:0 y1:0, x2:0 y2:1, stop:0 green, stop:1 white);"
                             "}")

        # create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # create labels
        label_head = QLabel("HEAD")
        label_name1 = QLabel(name1)
        label_torso = QLabel("TORSO")
        label_name2 = QLabel(name2)
        lable_level = QLabel(f"Lv:  {min_level}-{max_level}")
        # set font of all labels to custom and align them to center
        for label in [label_head, label_name1, label_torso, label_name2, lable_level]:
            font = QFont(families[0], 12)
            font.setBold(label.text() == 'HEAD' or label.text() == 'TORSO')
            label.setFont(font)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # add labels to result with appropriate stretches
        layout.addStretch()
        layout.addWidget(label_head)
        layout.addWidget(label_name1)
        layout.addStretch()
        layout.addWidget(label_torso)
        layout.addWidget(label_name2)
        layout.addStretch()
        layout.addWidget(lable_level)
        layout.addStretch()

        result.setLayout(layout)

        return result

    def get_image_label(self, url):
        image_label = QLabel()
        self.set_pixmap_from_url(image_label,
                                 url,
                                 self.SPRITE_SIZE)
        return image_label


class _SingleTab(_IFFTBaseTab):

    def __init__(self, image_size: int, margin: int):
        super().__init__(image_size, margin)

        self.sprite1, self.cbox1 = self.init_input()
        self.sprite2, self.cbox2 = self.init_input()

        self.fuse_button = QPushButton("Fuse")
        self.fuse_button.pressed.connect(self.update)

        self.input.addStretch()
        self.input.addWidget(self.sprite1)
        self.input.addWidget(self.cbox1)
        self.input.addStretch()
        self.input.addWidget(self.sprite2)
        self.input.addWidget(self.cbox2)
        self.input.addStretch()
        self.input.addWidget(self.fuse_button)
        self.input.addStretch()

    def init_input(self):
        sprite = QLabel()
        sprite.setFixedHeight(self.SPRITE_SIZE)
        sprite.setFixedWidth(self.SPRITE_SIZE)
        sprite.setStyleSheet(".QLabel{"
                             "     border: 5px ridge gray;"
                             "}")
        cbox = QComboBox()
        cbox.addItems(utils.get_names())
        cbox.currentTextChanged.connect(
            lambda: self.set_pixmap_from_url(
                sprite,
                utils.get_sprite_url(
                    cbox.currentText()
                )
            )
        )
        self.set_pixmap_from_url(
            sprite,
            utils.get_sprite_url(cbox.currentText())
        )
        return sprite, cbox

    def update(self):
        pkmn1 = self.cbox1.currentText()
        pkmn2 = self.cbox2.currentText()

        urlsAB, urlsBA = utils.get_fusion_urls(pkmn1, pkmn2)
        self.clear_layout(self.fusion_space)

        self.fusion_space.addStretch()
        for urls in [urlsAB, urlsBA]:
            grid = QGridLayout()
            for i, (info, url) in enumerate(urls):
                box = QHBoxLayout()
                image = self.get_image_label(url)
                text = self.get_info_box(*info)
                box.addStretch()
                box.addWidget(image)
                box.addWidget(text)
                box.addStretch()

                grid.addLayout(box, int(i/5), i % 5)
            self.fusion_space.addLayout(grid)
            self.fusion_space.addStretch()


class _BatchTab(_IFFTBaseTab):

    def __init__(self, image_size: int, margin: int):
        super().__init__(image_size, margin)

        self.cbox = QComboBox()
        self.cbox.addItems(utils.get_names())

        self.add = QPushButton("Add")
        self.plist = QListWidget()
        self.add.pressed.connect(self.update_list)

        self.remove = QPushButton("Remove")
        self.remove.pressed.connect(self.remove_from_list)

        self.run = QPushButton("Run")
        self.run.pressed.connect(self.mix)

        self.input.addStretch()
        self.input.addWidget(self.cbox)
        self.input.addWidget(self.add)
        self.input.addWidget(self.remove)
        self.input.addStretch()
        self.input.addWidget(self.plist)
        self.input.addStretch()
        self.input.addWidget(self.run)
        self.input.addStretch()

    def remove_from_list(self) -> None:
        indexes_to_remove = [item.row() for item in self.plist.selectedIndexes()]
        for index in indexes_to_remove:
            item = self.plist.takeItem(index).text()
            if self.cbox.findText(item, Qt.MatchFlag.MatchExactly) == -1:
                for evo in utils.get_evolution_list(item):
                    self.cbox.addItem(evo['name'])

    def update_list(self) -> None:
        """
        Adds the Pokemon selected in the cbox to the list.
        If the Pokemon (ar any of its evolutionary line) are already present,
        add them and remove them from the cbox list
        """
        item_to_add = self.cbox.currentText()
        evo_list = [evo['name'] for evo in utils.get_evolution_list(item_to_add)]

        # check if any evolution is already in the list
        for evo in evo_list:
            if self.plist.findItems(evo, Qt.MatchFlag.MatchExactly):
                # if it is, remove all of them from the list, then break the cycle
                for e in evo_list:
                    self.cbox.removeItem(self.cbox.findText(e))
                break
        self.plist.addItem(item_to_add)

    def mix(self):
        result = []
        for i in range(self.plist.count()):
            result.append(self.plist.item(i).text())
        result = list(combinations(result, 2))
        self.clear_layout(self.fusion_space)

        for pkmn1, pkmn2 in result:
            urlsAB, urlsBA = utils.get_fusion_urls(pkmn1, pkmn2)

            self.fusion_space.addStretch()
            for urls in [urlsAB, urlsBA]:
                grid = QGridLayout()
                for i, (info, url) in enumerate(urls):
                    box = QHBoxLayout()
                    image = self.get_image_label(url)
                    text = self.get_info_box(*info)
                    box.addStretch()
                    box.addWidget(image)
                    box.addWidget(text)
                    box.addStretch()

                    grid.addLayout(box, int(i/5), i % 5)
                self.fusion_space.addLayout(grid)
                self.fusion_space.addStretch()
