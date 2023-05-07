import logging
import sys
from itertools import combinations
from random import Random

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFontDatabase, QFont
from PyQt6.QtWidgets import QComboBox, QVBoxLayout, QPushButton, QListWidget, QLabel, QWidget, QHBoxLayout, \
    QTabWidget, QGridLayout, QScrollArea, QLayout, QGraphicsColorizeEffect, QApplication, QToolTip

from data import utils
from data.pokemon import Pokemon
from gui.dialog import ConnectionErrorDialog
from ifft.data import pokedex


class IFFTTabs(QTabWidget):
    """
    Custom QTabWidget widget, it just creates the 2 tabs and adds them to itself
    """

    def __init__(self):
        super().__init__()

        self.addTab(_SingleTab(), "Single")
        self.addTab(_BatchTab(), "Batch")


class _IFFTBaseTab(QWidget):
    """
    Base custom tab, it contains common widgets (input and output layouts)
    and common methods
    """

    def __init__(self):
        super().__init__()

        # init custom font
        font_id = QFontDatabase.addApplicationFont("pokemon_pixel_font.ttf")
        assert font_id >= 0, 'Could not find font'
        self.families = QFontDatabase.applicationFontFamilies(font_id)

        # Create and add the root panel for the tab
        self.panel = QHBoxLayout()
        self.panel.setAlignment(Qt.AlignmentFlag.AlignLeading)
        self.setLayout(self.panel)

        # Create the input layout and add it to a QWidget (so we can set the size)
        input_container = QWidget()
        self.input_layout = QVBoxLayout()
        input_container.setLayout(self.input_layout)
        input_container.setFixedWidth(2 * utils.MARGIN + utils.SPRITE_SIZE)
        self.panel.addWidget(input_container)

        # Create a scroll area (so if too many outputs are added we can scroll)
        output_scroll = QScrollArea()
        # Create the output layout and add it to a QWidget (so we can set the size)
        output_container = QWidget()
        self.output_layout = QVBoxLayout()
        output_container.setLayout(self.output_layout)
        output_container.setFixedWidth(10 * utils.SPRITE_SIZE)

        # Add output container to scroll area and set vertical scrollbar always displaying
        output_scroll.setWidget(output_container)
        output_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        output_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        output_scroll.setWidgetResizable(True)
        self.panel.addWidget(output_scroll)

    def clear_layout(self, layout: QLayout):
        """ Remove all child widgets from a layout """
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    self.clear_layout(child.layout())

    def set_pixmap_from_url(self, label: QLabel, url: str):
        """
        Given a QLabel and an url, it sets the image of the label to that url.
        If status code is 404 NotFound, we try alternative urls.
        """
        try:
            response = requests.get(url)
            pixmap = QPixmap()
            n = url.split("/")[-1].split('.')[0]

            if response.status_code == 404:
                if 'black-white' in url:
                    response = requests.get(url.replace("black-white", "sun-moon"))
                else:
                    response = requests.get(url.replace("main/CustomBattlers", "master/Battlers"))
                    if response.status_code == 404:
                        response = requests.get(url.replace("main/CustomBattlers", f"master/Battlers/{n}"))
                    if response.status_code == 404:
                        response = requests.get(url.replace("main/CustomBattlers",
                                                            f"master/Battlers/{n}")
                                                   .replace("custom", "autogen"))

            logging.info(f"Final url: {url.split('Aegide/')[-1]}")

            pixmap.loadFromData(response.content)

            pixmap = pixmap.scaledToHeight(utils.SPRITE_SIZE)

            label.setPixmap(pixmap)
        except requests.exceptions.ConnectionError:
            # Could not connect to the internet, show an error dialog,
            # then close the app when "Close" is clicked.
            dlg = ConnectionErrorDialog(self)
            dlg.exec()
            sys.exit()

    def get_info_box(self, pkmn1: Pokemon, pkmn2: Pokemon):
        """
        Creates a Vertical layout displaying the name of the 2 fused Pokemons,
        including which part is which, and min-max level of that particular evo
        :param pkmn1: "head" pokemon
        :param pkmn2: "body" pokemon
        :return:a QVBoxLayout containing the labels formatted
        """

        result = QWidget()
        # Set background style of info widget
        color1 = pkmn1.types[0]
        color2 = pkmn2.types[1] if len(pkmn2.types)>1 else pkmn2.types[0]
        result.setStyleSheet(".QWidget{ "
                             f" width: {int(utils.SPRITE_SIZE/2)};"
                             f" height: {utils.SPRITE_SIZE};"
                             "  border-radius: 15px; "
                             "  border-bottom-left-radius: 3px;"
                             "  background: qlineargradient( x1:0 y1:0, "
                             "                               x2:0 y2:1, "
                             f"                              stop:0 {color1.value}, "
                             f"                              stop:1 {color2.value});"
                             "}")

        # create layout
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # create labels
        label_head = QLabel("HEAD")
        label_name1 = QLabel(pkmn1.name.capitalize())
        label_body = QLabel("BODY")
        label_name2 = QLabel(pkmn2.name.capitalize())
        min_level = max(pkmn1.min_level, pkmn2.min_level)
        max_level = min(pkmn1.max_level, pkmn2.max_level)
        lable_level = QLabel(f"LEVEL")
        lable_values = QLabel(f"{min_level}-{max_level}")
        # set font of all labels to custom and align them to center
        for label in [label_head, label_name1, label_body, label_name2, lable_level, lable_values]:
            font = QFont(self.families[0], 12)

            if label.text() in ['HEAD', 'BODY', 'LEVEL']:
                font.setBold(True)
            else:
                color_effect = QGraphicsColorizeEffect()
                color_effect.setColor(Qt.GlobalColor.white)
                label.setGraphicsEffect(color_effect)

            label.setFont(font)

            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # add labels to result with appropriate stretches
        layout.addStretch()
        layout.addWidget(label_head)
        layout.addWidget(label_name1)
        layout.addStretch()
        layout.addWidget(label_body)
        layout.addWidget(label_name2)
        layout.addStretch()
        layout.addWidget(lable_level)
        layout.addWidget(lable_values)
        layout.addStretch()

        result.setLayout(layout)

        return result

    def get_image_label(self, url):
        image_label = QLabel()
        self.set_pixmap_from_url(image_label,
                                 url)
        return image_label

    def display_fusions(self, pkmn1: str, pkmn2: str):

        urls_ab, urls_ba = utils.get_fusion_urls(pkmn1, pkmn2)

        self.output_layout.addStretch()
        for urls in [urls_ab, urls_ba]:
            grid_container = QWidget()
            grid_container.setObjectName('evoline')
            grid_container.setStyleSheet('.QWidget#evoline{'
                                         '     border: 5px ridge gray;'
                                         '}')
            grid = QGridLayout()
            for i, (pkmn1, pkmn2, url) in enumerate(urls):
                box_container = QWidget()
                box = QHBoxLayout()
                image = self.get_image_label(url)
                text = self.get_info_box(pkmn1,
                                         pkmn2)

                QToolTip.setFont(QFont(self.families[0], 12))
                hp = int(pkmn1.hp * 2 / 3 + pkmn2.hp / 3)
                attack = int(pkmn2.attack * 2 / 3 + pkmn1.attack / 3)
                defence = int(pkmn2.defence * 2 / 3 + pkmn1.defence / 3)
                spatk = int(pkmn1.spatk * 2 / 3 + pkmn2.spatk / 3)
                spdef = int(pkmn1.spdef * 2 / 3 + pkmn2.spdef / 3)
                speed = int(pkmn2.speed * 2 / 3 + pkmn1.speed / 3)

                color1 = pkmn1.types[0]
                color2 = pkmn2.types[1] if len(pkmn2.types) > 1 else pkmn2.types[0]
                box_container.setToolTip(f'<h1 style="background-color:{color1.value};color: white;">{color1.name}</h1>'
                                         + (f'<h1 style="background-color:{color2.value};color: white;">{color2.name}</h1>' if color2 != color1 else '') +
                                         f'<p>HP: {hp}</p>'
                                         f'<p>ATK: {attack}</p>'
                                         f'<p>DEF: {defence}</p>'
                                         f'<p>SP.ATK: {spatk}</p>'
                                         f'<p>SP.DEF: {spdef}</p>'
                                         f'<p>SPEED: {speed}</p>'
                                         f'<p>TOTAL: {hp+attack+defence+spatk+spdef+speed}</p>')

                box.addStretch()
                box.addWidget(image)
                box.addWidget(text)
                box.addStretch()
                box_container.setLayout(box)

                grid.addWidget(box_container, int(i / 5), i % 5)
            grid_container.setLayout(grid)
            if len(urls) > 0:
                self.output_layout.addWidget(grid_container)
                self.output_layout.addStretch()


class _SingleTab(_IFFTBaseTab):

    def __init__(self):
        super().__init__()

        self.info_box = QVBoxLayout()
        font = QFont(self.families[0], 12)

        info_label = QLabel("<b>INFO</b>")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_message = QLabel("You can see typing and stats of a Pokemon hovering it with the mouse.\n\n"
                              "To keep the application light-weight, "
                              "the sprites are downloaded on every fusion request.")
        info_message.setWordWrap(True)
        info_label.setFont(font)
        info_message.setFont(font)
        self.info_box.addWidget(info_label)
        self.info_box.addWidget(info_message)

        self.sprite1, self.cbox1, self.random1 = self.init_input()
        self.sprite2, self.cbox2, self.random2 = self.init_input()

        self.fuse_button = QPushButton("Fuse")
        self.fuse_button.pressed.connect(self.update)

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
        cbox.addItems(pokedex.get_names())
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

        def get_random():
            items_n = cbox.count()
            idx = Random().randint(0, items_n-1)
            cbox.setCurrentIndex(idx)
            self.set_pixmap_from_url(
                sprite,
                utils.get_sprite_url(cbox.currentText())
            )

        random = QPushButton('Random')
        random.clicked.connect(get_random)
        return sprite, cbox, random

    def update(self):
        pkmn1 = self.cbox1.currentText()
        pkmn2 = self.cbox2.currentText()

        self.clear_layout(self.output_layout)

        self.display_fusions(pkmn1, pkmn2)


class _BatchTab(_IFFTBaseTab):

    def __init__(self):
        super().__init__()

        self.warn_box = QVBoxLayout()
        font = QFont(self.families[0], 12)

        warn_label = QLabel("WARNING")
        warn_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warn_message = QLabel("The time this takes, grows exponentially with the number of Pokemons added.\n"
                              "We discourage fusing more than 4 at a time to avoid excessive loading times.")
        warn_message.setWordWrap(True)
        color_effect = QGraphicsColorizeEffect()
        color_effect.setColor(Qt.GlobalColor.red)
        warn_label.setGraphicsEffect(color_effect)
        warn_label.setFont(font)
        warn_message.setFont(font)
        self.warn_box.addWidget(warn_label)
        self.warn_box.addWidget(warn_message)

        self.cbox = QComboBox()
        self.cbox.addItems(pokedex.get_names())

        self.add = QPushButton("Add")
        self.plist = QListWidget()
        self.add.pressed.connect(self.update_list)

        self.random = QPushButton("Add Random")

        def get_random():
            items_n = self.cbox.count()
            idx = Random().randint(0, items_n-1)
            self.cbox.setCurrentIndex(idx)
            self.update_list()

        self.random.clicked.connect(get_random)

        self.remove = QPushButton("Remove")
        self.remove.pressed.connect(self.remove_from_list)

        self.run = QPushButton("Run")
        self.run.pressed.connect(self.mix)

        self.input_layout.addStretch()
        self.input_layout.addLayout(self.warn_box)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.cbox)
        self.input_layout.addWidget(self.add)
        self.input_layout.addWidget(self.random)
        self.input_layout.addWidget(self.remove)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.plist)
        self.input_layout.addStretch()
        self.input_layout.addWidget(self.run)
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
        QApplication.processEvents()
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

        for pkmn1, pkmn2 in result:
            QApplication.processEvents()
            self.display_fusions(pkmn1, pkmn2)
            self.repaint()
