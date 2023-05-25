from typing import List

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtNetwork import QNetworkAccessManager
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QGraphicsColorizeEffect, QGridLayout, QToolTip, \
    QStyleOption, QStyle

from data import utils
from data.pokemon import FusedPokemon


class _Url2LabelMap:

    def __init__(self):
        self._map = dict()

    def put(self, url: str, label: QLabel):
        val = self._map.get(url) if self._map.get(url) else []
        val.append(label)
        self._map[url] = val

    def delete(self, url: str) -> QLabel:
        return self._map.pop(url)[0]

    def get(self, url: str):
        return self._map.get(url, [])

    def keys(self):
        return self._map.keys()


URL2LABEL = _Url2LabelMap()


class CustomWidget(QWidget):
    """
    Base class of custom QWidgets.
    Classes must implement this becase of paintEvent.
    Without this method, self.setStyleSheet(...) does not work.
    """

    def paintEvent(self, pe):
        option = QStyleOption()
        option.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget,
                                   option, painter, self)


class EvolineWidget(CustomWidget):
    """
    A Grid containing n FusionWidgets.
    The Grid has a grey border and the items are 5 per row.
    """

    def __init__(self, urls: List[FusedPokemon]):
        super().__init__()
        # Set name (so that setting StyleSheet does not affect children widgets)
        self.setObjectName('evoline')
        # And Style Sheet (a gray border around evoline) TODO might want to make it look better
        self.setStyleSheet('QWidget#evoline{'
                           '     border: 5px ridge gray;'
                           '}')

        # Create a grid where to put each fusion widget, in rows of 5
        grid = QGridLayout()
        self.fusion_widgets = []
        for i, fusion in enumerate(urls):
            self.fusion_widgets.append(FusionWidget(fusion))
            grid.addWidget(self.fusion_widgets[i], int(i / 5), i % 5)

        self.setLayout(grid)

    def fetch_images(self, nam: QNetworkAccessManager):
        for widget in self.fusion_widgets:
            widget.fetch_image(nam)


class FusionWidget(CustomWidget):
    """
    A Widget containing a QLabel with the image of a fused pokemon
    and an InfoWidget with info about that pokemon.
    The items are disposed horizontally
    """

    def __init__(self, fusion: FusedPokemon):
        super().__init__()
        self.fusion = fusion

        QToolTip.setFont(utils.get_font())
        self.setToolTip(f'<h1 style="background-color:{fusion.types[0].value}; color: white;">'
                        f'  {fusion.types[0].name}'
                        f'</h1>'
                        + (f'<h1 style="background-color:{fusion.types[1].value};color: white;">'
                           f'   {fusion.types[1].name}'
                           f'</h1>' if fusion.types[1] != fusion.types[0] else '') +
                        f'<p>HP: {fusion.hp}</p>'
                        f'<p>ATK: {fusion.attack}</p>'
                        f'<p>DEF: {fusion.defense}</p>'
                        f'<p>SP.ATK: {fusion.special_attack}</p>'
                        f'<p>SP.DEF: {fusion.special_defense}</p>'
                        f'<p>SPEED: {fusion.speed}</p>'
                        f'<p>'
                        f'  TOTAL: {fusion.hp + fusion.attack + fusion.defense + fusion.special_attack + fusion.special_defense + fusion.speed}'
                        f'</p>')

        # Create a horizontal layout
        layout = QHBoxLayout()

        # Then create an image label and an info widget
        self.image = QLabel()
        self.info_box = InfoWidget(fusion)

        # Add everything to the layout
        layout.addStretch()
        layout.addWidget(self.image)
        layout.addWidget(self.info_box)
        layout.addStretch()

        # Set the horizontal layout as the layout of the widget
        self.setLayout(layout)

    def fetch_image(self, nam: QNetworkAccessManager):
        url = self.fusion.get_sprite_url()
        URL2LABEL.put(url, self.image)
        self.fusion.fetch_image(nam)


class InfoWidget(CustomWidget):
    """
    A Widget displaying data about a fused pokemon
    """

    def __init__(self, fusion: FusedPokemon):
        super().__init__()

        # Set style sheet.
        # This sets background appearance and color based on fused pokemon types.
        self.setObjectName('info')
        self.setStyleSheet("QWidget#info{ "
                           f" width: {int(utils.SPRITE_SIZE/2)}; "
                           f" height: {utils.SPRITE_SIZE}; "
                           "  border-radius: 15px; "
                           "  border-bottom-left-radius: 3px;"
                           "  background: qlineargradient( x1:0 y1:0, "
                           "                               x2:0 y2:1, "
                           f"                              stop:0 {fusion.types[0].value}, "
                           f"                              stop:1 {fusion.types[1].value});"
                           "}")

        # Create a center-aligned layout (to add labels to)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create labels (key, value) with info
        label_head_key = QLabel("HEAD")
        label_head_value = QLabel(fusion.head.capitalize())

        label_body_key = QLabel("BODY")
        label_body_value = QLabel(fusion.body.capitalize())

        label_level_key = QLabel("LEVEL")
        label_level_value = QLabel(f"{fusion.min_level}-{fusion.max_level}")

        # Set font of all key labels to custom and bold and alignment to center
        font = utils.get_font(bold=True)
        for key_label in [label_head_key, label_body_key, label_level_key]:
            key_label.setFont(font)
            key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Set font of all value labels to custom and white and alignment to center
        font = utils.get_font()
        for value_label in [label_head_value, label_body_value, label_level_value]:
            value_label.setFont(font)
            color_effect = QGraphicsColorizeEffect()
            color_effect.setColor(Qt.GlobalColor.white)
            value_label.setGraphicsEffect(color_effect)
            value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # add labels to layout with appropriate stretches
        layout.addStretch()
        layout.addWidget(label_head_key)
        layout.addWidget(label_head_value)
        layout.addStretch()
        layout.addWidget(label_body_key)
        layout.addWidget(label_body_value)
        layout.addStretch()
        layout.addWidget(label_level_key)
        layout.addWidget(label_level_value)
        layout.addStretch()

        # Set layout as layout of widget
        self.setLayout(layout)
