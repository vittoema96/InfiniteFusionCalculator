from PyQt6.QtWidgets import QApplication

from ifft.gui.window import IFFTWindow


def main():
    app = QApplication([])
    window = IFFTWindow()
    window.show()
    app.exec()


if __name__ == '__main__':
    main()
