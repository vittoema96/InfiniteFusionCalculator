import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout

from ifft.gui.tabs import IFFTTabs

#  TODO:
#       - Avoid displaying copies of same (ex: bulbasaur+bulbasaur=2*same evoline)
#           * In Batch mode don't count copies for 2x pokemon
#               QList<QListWidgetItem*> items = ui->listWidget->selectedItems();
#               foreach(QListWidgetItem* item, items){
#                   ui->listWidget->removeItemWidget(item);
#                   delete item; // Qt documentation warnings you to destroy item to effectively remove it from QListWidget.
#               }
#       - Change MIN_LEVEL from 0 to 1 in data.csv
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
    output_panel should contain 6 sprites (with borders and text, so margin size is doubled).
    input_panel is not relevant for height calculation."""
    HEIGHT: int = 6 * SPRITE_SIZE + 2 * (7 * MARGIN)

    def __init__(self):
        super().__init__()
        logging.basicConfig(level=logging.INFO)

        # Set title, size and pos
        self.setWindowTitle("IFFT")
        self.setFixedWidth(self.WIDTH)
        self.setFixedHeight(self.HEIGHT)

        qr = self.frameGeometry()
        cp = self.screen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.X = qr.topLeft().x()
        self.Y = qr.topLeft().y()

        self.panel = QVBoxLayout()
        self.tabs = IFFTTabs(self.SPRITE_SIZE, self.MARGIN)

        self.panel.addWidget(self.tabs)
        self.setLayout(self.panel)
        self.show()

        logging.info(f"Set window 'IFFT' to ({self.X}, {self.Y})")






