from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *


class QGameControl(QWidget):
    def __init__(self, slot_id, parent):
        super().__init__(parent)

        self.__slot_id = slot_id

        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.game_select = QComboBox()
        self.game_select.setFocusPolicy(Qt.NoFocus)
        self.main_layout.addWidget(self.game_select)

    def resetSelector(self, names, handler):
        try:
            self.game_select.currentIndexChanged.disconnect()
        except TypeError:
            ...
        self.game_select.clear()
        self.game_select.addItems(names)
        self.game_select.setCurrentIndex(0)
        self.game_select.currentIndexChanged.connect(handler)

    def selectGame(self, id):
        self.game_select.setCurrentIndex(id)



