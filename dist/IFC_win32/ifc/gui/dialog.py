from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel
import webbrowser

from data import utils


class ConnectionErrorDialog(QDialog):
    """
    Dialog box used to notify the user that the app
    cannot establish an internet connection
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Connection Error")

        close_button = QDialogButtonBox.StandardButton.Close
        self.buttonBox = QDialogButtonBox(close_button)

        self.layout = QVBoxLayout()
        message = QLabel("Could not connect to the internet, please check your connection and rerun the app.")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class UpdateDialog(QDialog):
    """
    Dialog box used to notify the user that an update exists on the github page
    """
    def __init__(self, new_version: str, parent=None):
        super().__init__(parent)

        self.setWindowTitle("An update is available")

        button = QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QDialogButtonBox(button)
        self.buttonBox.accepted.connect(self.go_to_github)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QVBoxLayout()
        message = QLabel(f"An update is available for the application.\n"
                         f"\n"
                         f"Current Version: {utils.VERSION}\n"
                         f"New Version: {new_version}\n"
                         f"\n"
                         f"Do you want to visit the github page?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def go_to_github(self):
        webbrowser.open('https://github.com/vittoema96/InfiniteFusionCalculator')