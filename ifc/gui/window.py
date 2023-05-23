import logging

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QTabWidget

from data import utils

from gui.tabs.batch import BatchTab
from gui.tabs.single import SingleTab
from gui.tabs.type import TypeTab

#  TODO:
#       - Handle lowercase/UpperCase pokemon names
#       ? Check if single species evolution stop is possible (THIS CHANGES EVERYTHING, MIGHT NOT IMPLEMENT)


class IFCWindow(QMainWindow):

    """
    Width of the window. 
    Window is divided in input_panel and output_panel.
    input_panel is (SPRITE_SIZE + 2 * MARGIN) wide,
    output_panel is (10 * SPRITE_SIZE + 11 * MARGIN) wide
    """
    WIDTH: int = (utils.SPRITE_SIZE + 2 * utils.MARGIN) + \
                 (10 * utils.SPRITE_SIZE + 11*utils.MARGIN)

    """
    Height of the window.
    output_panel should contain 6 sprites (with 6+1 margins).
    input_panel is not relevant for height calculation."""
    HEIGHT: int = 6 * utils.SPRITE_SIZE + 2 * (7 * utils.MARGIN)

    def __init__(self):
        super().__init__()
        # Init logging
        logging.basicConfig(level=logging.INFO)

        # Set title, size and pos
        self.setWindowTitle(utils.TITLE)
        self.setWindowIcon(QIcon('icon.ico'))
        self.setFixedWidth(self.WIDTH)
        self.setFixedHeight(self.HEIGHT)

        # Define container layout and the tabs widget
        self.tabs = QTabWidget()
        self.tabs.addTab(SingleTab(), "Single")
        self.tabs.addTab(BatchTab(), "Batch")
        self.tabs.addTab(TypeTab(), "Type")

        # And add them to the window
        self.setCentralWidget(self.tabs)

        # Now show it
        self.show()
