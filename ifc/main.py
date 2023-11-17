from PyQt6.QtWidgets import QApplication
from ifc.gui.window import IFCWindow


def main():
    app = QApplication([])
    window = IFCWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
