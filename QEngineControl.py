from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from ConsoleWidget import QConsoleWidget


class QEngineControl(QWidget):
    def __init__(self, slot_id, parent):
        super().__init__(parent)

        self.__slot_id = slot_id

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.controls_layout = QHBoxLayout()
        self.main_layout.addLayout(self.controls_layout)

        self.engine_select = QComboBox()
        self.engine_select.setFocusPolicy(Qt.NoFocus)
        self.controls_layout.addWidget(self.engine_select)

        self.show_engine_io_checkbox = QCheckBox("Show engine IO")
        self.show_engine_io_checkbox.setFocusPolicy(Qt.NoFocus)
        self.show_engine_io_checkbox.setCheckState(
            self.parent().core.get_show_engine_io(self.__slot_id))
        self.show_engine_io_checkbox.stateChanged.connect(
            lambda value: self.parent().core.set_show_engine_io(self.__slot_id, value))
        self.controls_layout.addWidget(self.show_engine_io_checkbox)

        self.kill_button = QPushButton("Kill")
        self.kill_button.clicked.connect(lambda: self.__engine.kill())
        self.controls_layout.addWidget(self.kill_button)

        self.console_widget = QConsoleWidget()
        self.main_layout.addWidget(self.console_widget)

        self.__engine = None


    def resetSelector(self, names, id, handler):
        try:
            self.engine_select.currentIndexChanged.disconnect()
        except TypeError:
            ...
        self.engine_select.clear()
        self.engine_select.addItems(names)
        self.engine_select.setCurrentIndex(id)
        self.engine_select.currentIndexChanged.connect(handler)

    def attachEngine(self, engine):
        self.__engine = engine
        try:
            self.__engine.con_print.disconnect()
        except TypeError:
            ...
        self.__engine.con_print.connect(self.console_widget.print)
        self.console_widget.setInputHandler(lambda text: self.__engine.send_command(text))

    def selectEngine(self, id):
        self.engine_select.setCurrentIndex(id)




