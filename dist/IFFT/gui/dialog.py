from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel


class ConnectionErrorDialog(QDialog):
    """
    Dialog box used to notify the user that the app
    cannot establish an internet connection
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Connection Error")

        QBtn = QDialogButtonBox.StandardButton.Close
        self.buttonBox = QDialogButtonBox(QBtn)

        self.layout = QVBoxLayout()
        message = QLabel("Could not connect to the internet, please check your connection and rerun the app.")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
