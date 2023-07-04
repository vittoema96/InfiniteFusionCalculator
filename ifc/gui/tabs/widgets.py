from typing import List, Callable, Optional

from PyQt6.QtCore import Qt, pyqtSignal
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

    def __init__(self, urls: List[FusedPokemon], click_callback: Callable):
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
            self.fusion_widgets.append(FusionWidget(fusion, click_callback))
            grid.addWidget(self.fusion_widgets[i], int(i / 5), i % 5)

        self.setLayout(grid)

    def fetch_images(self, nam: QNetworkAccessManager):
        for widget in self.fusion_widgets:
            widget.fetch_image(nam)

    def update_tooltips(self, fusion: Optional[FusedPokemon] = None):
        for widget in self.fusion_widgets:
            widget.update_tooltip(fusion)


class FusionWidget(CustomWidget):
    """
    A Widget containing a QLabel with the image of a fused pokemon
    and an InfoWidget with info about that pokemon.
    The items are disposed horizontally
    """
    press_pos = None
    border_style = "border: 3px solid red;"

    def __init__(self, fusion: FusedPokemon, click_callback: Callable):
        super().__init__()

        self.selected = False

        self.click_callback = click_callback
        self.fusion = fusion
        self.setFixedWidth(int(utils.SPRITE_SIZE * 3 / 2))
        # Set style sheet.
        # This sets background appearance and color based on fused pokemon types.
        self.setObjectName('info')
        self.setStyleSheet("QWidget#info{ "
                           "  border-radius: 15px; "
                           "  background: qlineargradient( x1:0 y1:0, "
                           "                               x2:0 y2:1, "
                           f"                              stop:0 {fusion.types[0].value}, "
                           f"                              stop:1 {fusion.types[1].value});"
                           "}")

        QToolTip.setFont(utils.get_font())
        self.update_tooltip(None)

        # Create a horizontal layout
        layout = QVBoxLayout()

        # Then create an image label and an info widget
        self.pokemon_names_label = QLabel(fusion.head.capitalize()+' / '+fusion.body.capitalize())
        self.pokemon_names_label.setFont(utils.get_font(bold=True))
        self.image = QLabel()
        self.level_key_label = QLabel("LEVEL")
        self.level_key_label.setFont(utils.get_font(bold=True))
        self.level_value_label = QLabel(f"{fusion.min_level}-{fusion.max_level}")

        for label in [self.pokemon_names_label, self.image, self.level_key_label, self.level_value_label]:
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add everything to the layout
        layout.addStretch()
        layout.addWidget(self.pokemon_names_label)
        layout.addStretch()
        layout.addWidget(self.image)
        layout.addStretch()
        layout.addWidget(self.level_key_label)
        layout.addWidget(self.level_value_label)
        layout.addStretch()

        # Set the horizontal layout as the layout of the widget
        self.setLayout(layout)

    def fetch_image(self, nam: QNetworkAccessManager):
        url = self.fusion.get_sprite_url()
        URL2LABEL.put(url, self.image)
        self.fusion.fetch_image(nam)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.press_pos = event.pos()

    def mouseReleaseEvent(self, event):
        # ensure that the left button was pressed *and* released within the
        # geometry of the widget; if so, emit the signal;
        if (self.press_pos is not None
                and event.button() == Qt.MouseButton.RightButton
                and event.pos() in self.rect()):
            self.click_callback(self)
        self.press_pos = None

    def select(self):
        self.selected = True
        ss = self.styleSheet()
        ss = ss.replace('}', self.border_style+'}')
        self.setStyleSheet(ss)

    def deselect(self):
        self.selected = False
        try:
            ss = self.styleSheet()
            ss = ss.replace(self.border_style+'}', '}')
            self.setStyleSheet(ss)
        except RuntimeError as e:
            print(e)

    def update_tooltip(self, fusion: FusedPokemon = None):

        tooltip = f'<h1 style="background-color:{self.fusion.types[0].value}; ' \
                  f'    color: white;">' \
                  f'        {self.fusion.types[0].name}' \
                  f'</h1>'
        if self.fusion.types[1] != self.fusion.types[0]:
            tooltip += f'<h1 style="background-color:{self.fusion.types[1].value};' \
                       f'    color: white;">' \
                       f'       {self.fusion.types[1].name}' \
                       f'</h1>'

        def get_stat_line(stat_name: str, this: int, other: Optional[int]):
            style = ''
            difference = ''
            if other:
                color = 'green' if this >= other else 'red'
                style = f' style="color: {color}";'
                difference = this - other
                difference = '(' + (
                                 str(difference) if difference <= 0
                                 else '+' + str(difference)
                             ) + ')'

            return (
                f'<p{style}>'
                f'   {stat_name}: {this} {difference}'
                f'</p>'
            )

        tooltip += get_stat_line('HP', self.fusion.hp, fusion.hp if fusion else None)
        tooltip += get_stat_line('ATK', self.fusion.attack, fusion.attack if fusion else None)
        tooltip += get_stat_line('DEF', self.fusion.defense, fusion.defense if fusion else None)
        tooltip += get_stat_line('SP.ATK', self.fusion.special_attack, fusion.special_attack if fusion else None)
        tooltip += get_stat_line('SP.DEF', self.fusion.special_defense, fusion.special_defense if fusion else None)
        tooltip += get_stat_line('SPEED', self.fusion.speed, fusion.speed if fusion else None)
        tooltip += get_stat_line('TOTAL', self.fusion.total, fusion.total if fusion else None)

        self.setToolTip(tooltip)
