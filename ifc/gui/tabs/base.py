from typing import List, Optional, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QScrollArea, QLayout, QLabel

from data import utils
from data.stat_enum import Stat
from data.pokemon import Pokemon, FusedPokemon
from gui.tabs.widgets import GridWidget, FusionWidget


class IFCBaseTab(QWidget):
    """
    Base custom tab, meant to be an "abstract" tab to be implemented,
    it contains common widgets (input and output layouts)
    and common methods.
    """

    def __init__(self):
        super().__init__()

        # The currently selected Pokemon
        self.selected_pokemon = None

        self.layout = self._init_layout()
        self.setLayout(self.layout)

        self.input_container = self._init_input_container()
        self.input_layout = QVBoxLayout()
        self.input_container.setLayout(self.input_layout)

        self.output_container = self._init_output_container()
        self.output_layout = QVBoxLayout()
        self.output_container.widget().setLayout(self.output_layout)

        self.layout.addWidget(self.input_container)
        self.layout.addWidget(self.output_container)

    @staticmethod
    def _init_layout() -> QHBoxLayout:
        """
        Creates, aligns and sets the (QHBox)Layout of this widget
        """
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeading)
        return layout

    @staticmethod
    def _init_input_container() -> QWidget:
        """
        Create the container for the input layout
        """
        input_container = QWidget()
        input_container.setFixedWidth(4 * utils.MARGIN + utils.SPRITE_SIZE)

        return input_container

    @staticmethod
    def _init_output_container() -> QScrollArea:
        """
        Create the container of the output layout, a scroll area (so if too many outputs are added we can scroll)
        """
        output_scroll = QScrollArea()
        # Create the output layout and add it to a QWidget (so we can set the size)
        output_container = QWidget()
        output_container.setFixedWidth(12 * utils.SPRITE_SIZE)

        # Add output container to scroll area and set vertical scrollbar always displaying
        output_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        output_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        output_scroll.setWidgetResizable(True)
        output_scroll.setWidget(output_container)

        return output_scroll

    def select_pokemon(self, widget: Optional[FusionWidget]) -> None:
        """

        :param widget:
        """
        if self.selected_pokemon is not None:
            self.selected_pokemon.deselect()

        if widget is not None and widget != self.selected_pokemon:
            self.selected_pokemon = widget
            self.selected_pokemon.select()
        else:
            self.selected_pokemon = None
        # Now we need to update all tooltips (for confrontation)
        # Cycle over all evolines
        for i in range(self.output_layout.count()):
            # Get QWidgetItem and its widget (GridWidget)
            child = self.output_layout.itemAt(i)
            widget = child.widget()
            if widget and isinstance(widget, GridWidget):
                widget.update_tooltips(self.selected_pokemon.fusion if self.selected_pokemon else None)

    def set_info_message(self, message: str):
        """
        Sets an INFO message to the input panel
        :param message: The content of the message
        """
        self._set_message(header='INFO', message=message)

    def set_warning_message(self, message: str):
        """
        Sets a WARNING message to the input panel
        :param message: The content of the message
        """
        self._set_message(header='WARNING', color=QColor("red"), message=message)

    def _set_message(self, message: str, header: str = None, color: QColor = QColor("black")):
        """
        Base method to set a message for the input layout
        :param message: The message to display
        :param header: The title of the message (bold and may be a different color)
        :param color: The color of the header
        """
        assert self.input_layout is not None, "Can't set a message before calling super()"

        # Define the INFO box
        self.info_box = QVBoxLayout()

        # If there's a header (title), create and add it
        if header:
            header_label = QLabel(header)
            palette: QPalette = header_label.palette()
            palette.setColor(header_label.foregroundRole(), color)
            header_label.setPalette(palette)

            header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header_label.setFont(utils.get_font(bold=True))

            self.info_box.addWidget(header_label)

        # create and add the message
        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setFont(utils.get_font())
        self.info_box.addWidget(message_label)

        # add everything to input layout
        self.input_layout.addStretch()
        self.input_layout.addLayout(self.info_box)

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
            self.output_layout.addWidget(evoline_ab_widget)
        if display_ba:
            evoline_ba_widget = GridWidget(pkmn2, pkmn1, self.select_pokemon)
            self.output_layout.addWidget(evoline_ba_widget)

        self.output_layout.addStretch()
