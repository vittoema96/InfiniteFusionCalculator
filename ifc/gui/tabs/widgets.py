from typing import Callable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout, QGridLayout, QToolTip, \
    QStyleOption, QStyle, QPushButton, QComboBox

from data import utils
from data.stat_enum import Stat
from data.pokemon import FusedPokemon, Pokemon, AbstractPokemon
from gui.widget_painter import WidgetPainter


class CustomWidget(QWidget):
    """
    Base class of custom QWidgets.
    Classes must implement this because of paintEvent.
    Without this method, self.setStyleSheet(...) does not work.
    """

    def paintEvent(self, pe):
        option = QStyleOption()
        option.initFrom(self)
        painter = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget,
                                   option, painter, self)


class FetchingWidget(CustomWidget):

    def __init__(self, pokemon: AbstractPokemon, image: QLabel):
        super().__init__()
        self.pokemon = pokemon
        self.image = image

        url = self.pokemon.get_sprite_url()
        WidgetPainter().put(url, self.image)


class GridWidget(CustomWidget):
    """
    A Grid containing n FusionWidgets.
    The Grid has a grey border and the items are 5 per row.
    """

    def __init__(self, head: Pokemon, body: Pokemon, click_callback: Callable):
        super().__init__()
        # Set name (so that setting StyleSheet does not affect children widgets)
        self.setObjectName('evoline')
        # And Style Sheet (a gray border around evoline) TODO might want to make it look better
        self.setStyleSheet('QWidget#evoline{'
                           '     border: 5px ridge gray;'
                           '     background: black;'
                           '}')

        # Create a grid where to put each fusion widget, in rows of 5
        grid = QGridLayout()
        self.image_widgets = []
        for x, head_stage in enumerate([head] + head.evoline):
            for y, body_stage in enumerate([body] + body.evoline):
                reverse = len(head.evoline) < len(body.evoline)
                if x == 0 and y == 0:
                    continue
                elif y == 0:
                    widget = RawWidget(head.evoline[x-1], is_horiz=not reverse)
                elif x == 0:
                    widget = RawWidget(body.evoline[y-1], is_horiz=reverse)
                else:
                    widget = FusionWidget(FusedPokemon(head=head_stage, body=body_stage), click_callback)

                self.image_widgets.append(widget)
                if reverse:
                    grid.addWidget(widget, x, y)
                else:
                    grid.addWidget(widget, y, x)

        self.setLayout(grid)

    def update_tooltips(self, fusion: Optional[FusedPokemon] = None):
        for widget in self.image_widgets:
            if isinstance(widget, FusionWidget):
                widget.update_tooltip(fusion)


class RawWidget(FetchingWidget, QWidget):

    def __init__(self, pokemon: Pokemon, is_horiz: bool):
        super().__init__(pokemon, QLabel())
        layout = QHBoxLayout()
        if is_horiz:
            self.setFixedHeight(utils.SPRITE_SIZE)
        else:
            self.setFixedWidth(utils.SPRITE_SIZE)

        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.image)
        self.setLayout(layout)

        self.setObjectName('raw')
        self.setStyleSheet("QWidget#raw{ "
                           "  border-radius: 10px; "
                           "  background: white;"
                           "}")


class FusionWidget(FetchingWidget):
    """
    A Widget containing a QLabel with the image of a fused pokemon
    and an InfoWidget with info about that pokemon.
    The items are disposed horizontally
    """
    press_pos = None
    border_style = "border: 3px solid red;"

    def __init__(self, fusion: FusedPokemon, click_callback: Callable):
        super().__init__(fusion, QLabel())

        self.selected = False

        self.click_callback = click_callback
        self.fusion = fusion
        # Set style sheet.
        # This sets background appearance and color based on fused pokemon types.
        self.setObjectName('info')
        self.setStyleSheet("QWidget#info{ "
                           "  border-radius: 10px; "
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


class FuseButtonsWidget(QWidget):

    def __init__(self, update_output: Callable):
        super().__init__()
        bold_font = utils.get_font(bold=True)
        self.fuse_button = QPushButton("Fuse")
        self.random_button = QPushButton("Fuse Random")
        self.sort_by_text = QLabel("SORT BY")
        self.sort_by_cbox = QComboBox()

        self.fuse_button.setFont(bold_font)
        self.random_button.setFont(bold_font)
        self.sort_by_text.setFont(bold_font)
        self.sort_by_cbox.setFont(utils.get_font())

        self.sort_by_cbox.addItems([s.get_pretty_name() for s in Stat])

        self.fuse_button.pressed.connect(
            lambda: update_output(
                order=Stat.get(self.sort_by_cbox.currentText())
            )
        )
        self.random_button.pressed.connect(
            lambda: update_output(
                order=Stat.get(self.sort_by_cbox.currentText()),
                random=True
            )
        )

        layout = QVBoxLayout()

        layout.addStretch()
        layout.addWidget(self.sort_by_text)
        layout.addWidget(self.sort_by_cbox)
        layout.addStretch()
        layout.addWidget(self.fuse_button)
        layout.addStretch()
        layout.addWidget(self.random_button)
        layout.addStretch()

        self.setLayout(layout)
