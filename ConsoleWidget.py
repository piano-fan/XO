from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class QConsoleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.input_handler = None

        self.text = QPlainTextEdit(self)
        self.text.setReadOnly(True)

        self.input = QLineEdit(self)
        self.input.returnPressed.connect(self.onInput)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.text)
        self.layout.addWidget(self.input)

    def print(self, text):
        self.text.appendPlainText(text)

    def onInput(self):
        text = self.input.text()
        self.input.clear()
        if self.input_handler:
            self.input_handler(text)
        else:
            self.print("Input handler is None")

    def setInputHandler(self, handler):
        self.input_handler = handler
