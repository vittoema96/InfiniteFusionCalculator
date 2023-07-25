import logging
import re
from typing import List, Optional, Tuple

from PyQt6 import QtNetwork
from PyQt6.QtCore import Qt, QByteArray, QUrl
from PyQt6.QtGui import QPixmap, QPalette, QColor
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QLayout, QLabel

from data import utils
from data.stat_enum import Stat
from data.pokemon import Pokemon, FusedPokemon
from gui.tabs import widgets
from gui.tabs.widgets import GridWidget, FusionWidget


class IFCBaseTab(QWidget):
    """
    Base custom tab, meant to be an "abstract" tab to be implemented,
    it contains common widgets (input and output layouts)
    and common methods.
    """

    def __init__(self):
        super().__init__()

        self.selected_pokemon = None

        self.font = utils.get_font()
        self.bold_font = utils.get_font(bold=True)

        # Manager used to load sprites quickly
        self.nam = QtNetwork.QNetworkAccessManager()
        self.nam.finished.connect(self.on_image_result)

        # Create and add the root panel of the tab
        self.layout = QHBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeading)
        self.setLayout(self.layout)

        # Create the input layout and add it to a QWidget (so we can set the size)
        input_container = QWidget()
        input_container.setFixedWidth(4 * utils.MARGIN + utils.SPRITE_SIZE)
        self.input_layout = QVBoxLayout()
        input_container.setLayout(self.input_layout)

        # Create a scroll area (so if too many outputs are added we can scroll)
        output_scroll = QScrollArea()
        # Create the output layout and add it to a QWidget (so we can set the size)
        output_container = QWidget()
        output_container.setFixedWidth(12 * utils.SPRITE_SIZE)
        self.output_layout = QVBoxLayout()
        output_container.setLayout(self.output_layout)
        # Add output container to scroll area and set vertical scrollbar always displaying
        output_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        output_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        output_scroll.setWidgetResizable(True)
        output_scroll.setWidget(output_container)

        self.layout.addWidget(input_container)
        self.layout.addWidget(output_scroll)

    def select_pokemon(self, widget: Optional[FusionWidget]):
        if self.selected_pokemon is not None:
            self.selected_pokemon.deselect()

        if widget is not None and widget != self.selected_pokemon:
            self.selected_pokemon = widget
            self.selected_pokemon.select()
        else:
            self.selected_pokemon = None

        for i in range(self.output_layout.count()):
            child = self.output_layout.itemAt(i)
            if child.widget() is not None:
                widget = child.widget()
                if isinstance(widget, GridWidget):
                    widget.update_tooltips(self.selected_pokemon.fusion if self.selected_pokemon else None)

    def set_info_message(self, message: str):
        self._set_message(header='INFO', message=message)

    def set_warning_message(self, message: str):
        self._set_message(header='WARNING', color=QColor("red"), message=message)

    def _set_message(self, message: str, header: str = None, color: QColor = QColor("black")):
        assert self.input_layout is not None, "Can't set a message before calling super()"

        # Define the INFO box
        self.info_box = QVBoxLayout()

        if header:
            header_label = QLabel(f"<b>{header}</b>")
            palette: QPalette = header_label.palette()
            palette.setColor(header_label.foregroundRole(), color)
            header_label.setPalette(palette)

            header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_label.setFont(self.font)

            self.info_box.addWidget(header_label)

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setFont(self.font)

        self.info_box.addWidget(message_label)

        self.input_layout.addStretch()
        self.input_layout.addLayout(self.info_box)
        self.input_layout.addStretch()

    @staticmethod
    def clear_layout(layout: QLayout):
        """ Remove all child widgets from a layout """
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
                elif child.layout() is not None:
                    IFCBaseTab.clear_layout(child.layout())

    @staticmethod
    def set_pixmap(image: QByteArray, label: QLabel):
        """
        Given a QByteArray and a QLabel, it sets the image of the label.
        """
        pixmap = QPixmap()

        pixmap.loadFromData(image)

        pixmap = pixmap.scaledToHeight(utils.SPRITE_SIZE)

        label.setPixmap(pixmap)

    def on_image_result(self, reply: QtNetwork.QNetworkReply):
        """
        Called when the QNetworkAccessManager has finished downloading 1 image.
        Checks for failed download and tries all alternatives.

        :param reply:
        :return:
        """
        error = reply.error()
        url: str = reply.url().url()

        if url in widgets.URL2LABEL.keys():
            if error == QtNetwork.QNetworkReply.NetworkError.NoError:
                labels: List[QLabel] = widgets.URL2LABEL.get(url)

                bytes_string = reply.readAll()
                for label in labels:
                    self.set_pixmap(bytes_string, label)
                widgets.URL2LABEL.delete(url)

            else:
                if 'black-white' in url:
                    label = widgets.URL2LABEL.delete(url)
                    url = url.replace('black-white', 'sun-moon')
                    qurl = QtNetwork.QNetworkRequest(QUrl(url))
                    widgets.URL2LABEL.put(url, label)
                    self.nam.get(qurl)
                elif 'main/CustomBattlers' in url:
                    label = widgets.URL2LABEL.delete(url)
                    url = url.replace('main/CustomBattlers', 'master/Battlers')
                    qurl = QtNetwork.QNetworkRequest(QUrl(url))
                    widgets.URL2LABEL.put(url, label)
                    self.nam.get(qurl)
                elif re.search(r'master/Battlers/\d+.\d+\.png', url):
                    label = widgets.URL2LABEL.delete(url)
                    idx = url.split('/')[-1].split('.')[0]
                    url = url.replace('master/Battlers/', f'master/Battlers/{idx}/')
                    qurl = QtNetwork.QNetworkRequest(QUrl(url))
                    widgets.URL2LABEL.put(url, label)
                    self.nam.get(qurl)
                elif re.search(r'master/Battlers/\d+/\d+.\d+\.png', url):
                    label = widgets.URL2LABEL.delete(url)
                    url = url.replace('custom', 'autogen')
                    qurl = QtNetwork.QNetworkRequest(QUrl(url))
                    widgets.URL2LABEL.put(url, label)
                    self.nam.get(qurl)
                else:
                    logging.warning(f"Could not find an alternative url for '{url}'")

    def add_fusions(self, fusions: List[Tuple[Pokemon, Pokemon]], order: Stat, include_reverse: bool = True):
        self.output_layout.addStretch()
        couples = []
        for head, body in fusions:
            head = head.evoline[0]
            body = body.evoline[0]
            couples.append((head, body))
            if include_reverse and head != body:
                couples.append((body, head))
        couples = list(set(couples))

        def check_stat(t: Tuple[Pokemon, Pokemon]):
            max_val = 0
            for stage1 in t[0].evoline:
                for stage2 in t[1].evoline:
                    val = order.get_value(FusedPokemon(stage1, stage2))
                    if val > max_val:
                        max_val = val
            return max_val

        couples.sort(key=check_stat, reverse=True)

        for p1, p2 in couples:
            widget = GridWidget(p1, p2, self.select_pokemon)
            widget.fetch_images(self.nam)
            self.output_layout.addWidget(widget)
            self.output_layout.addStretch()


    def add_evoline_widgets(self,
                            pkmn1: Pokemon, pkmn2: Pokemon,
                            order: str = "TOTAL",
                            display_ab: bool = True, display_ba: bool = True):

        self.output_layout.addStretch()

        # Add the fusions to the visible list
        # Add ab and ba fusions separately only if they are enabled
        if display_ab:
            evoline_ab_widget = GridWidget(pkmn1, pkmn2, self.select_pokemon)
            evoline_ab_widget.fetch_images(self.nam)
            self.output_layout.addWidget(evoline_ab_widget)
        if display_ba:
            evoline_ba_widget = GridWidget(pkmn2, pkmn1, self.select_pokemon)
            evoline_ba_widget.fetch_images(self.nam)
            self.output_layout.addWidget(evoline_ba_widget)

        self.output_layout.addStretch()
