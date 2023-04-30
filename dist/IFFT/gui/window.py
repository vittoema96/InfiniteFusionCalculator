import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from data import utils
from ifft.gui.tabs import IFFTTabs

#  TODO:
#       - Handle lowercase/UpperCase pokemon names
#       ? Check if single species evolution stop is possible (THIS CHANGES EVERYTHING, MIGHT NOT IMPLEMENT)


class IFFTWindow(QWidget):

    """ The size that a Pokémon Sprite must have (1:1 ratio) """
    SPRITE_SIZE: int = 100
    """ Distance between two sprites """
    MARGIN: int = 10

    """
    Width of the window. 
    Window is divided in input_panel and output_panel.
    input_panel is (SPRITE_SIZE + 2 * MARGIN) wide,
    output_panel is (10 * SPRITE_SIZE + 11 * MARGIN) wide
    """
    WIDTH: int = (SPRITE_SIZE + 2 * MARGIN) + (10 * SPRITE_SIZE + 11*MARGIN)

    """
    Height of the window.
    output_panel should contain 6 sprites (with 6+1 margins).
    input_panel is not relevant for height calculation."""
    HEIGHT: int = 6 * SPRITE_SIZE + 2 * (7 * MARGIN)

    def __init__(self):
        super().__init__()
        # Init logging
        logging.basicConfig(level=logging.INFO)

        # Set title, size and pos
        self.setWindowTitle(utils.TITLE)
        self.setFixedWidth(self.WIDTH)
        self.setFixedHeight(self.HEIGHT)

        # Define container layout and the tabs widget
        self.panel = QVBoxLayout()
        self.tabs = IFFTTabs()

        # And add them to the window
        self.panel.addWidget(self.tabs)
        self.setLayout(self.panel)

        # Now show it
        self.show()
