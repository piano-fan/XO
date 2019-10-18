from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

from BoardWidget import QBoardWidget
from QEngineControl import QEngineControl
from QGameControl import QGameControl
from game import *


class QCoreWidget(QWidget):
    def __init__(self, core, parent=None):
        super().__init__(parent)

        self.core = core

        self.setWindowTitle("XO")

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.top_layout = QHBoxLayout()
        self.main_layout.addLayout(self.top_layout, 6)

        self.mid_layout = QHBoxLayout()
        self.main_layout.addLayout(self.mid_layout, 1)

        self.bottom_layout = QHBoxLayout()
        self.main_layout.addLayout(self.bottom_layout, 3)

        self.game_controls = [QGameControl(0, self), QGameControl(1, self)]
        self.update_game_controls()

        self.mid_layout.addWidget(self.game_controls[0])
        self.mid_layout.addWidget(self.game_controls[1])

        self.engine_controls = [QEngineControl(0, self), QEngineControl(1, self)]
        self.update_engine_controls()

        self.bottom_layout.addWidget(self.engine_controls[0])
        self.bottom_layout.addWidget(self.engine_controls[1])

        self.board_widgets = [QBoardWidget(self, 0), QBoardWidget(self, 1)]
        self.top_layout.addWidget(self.board_widgets[0], 6)
        self.top_layout.addWidget(self.board_widgets[1], 6)

        self.tools_layout = QVBoxLayout()
        self.top_layout.addLayout(self.tools_layout, 1)

        self.resize_slider = QSlider(Qt.Vertical)
        self.resize_slider.setRange(1, 255)
        self.resize_slider.setTickInterval(1)
        self.resize_slider.setValue(16)
        self.resize_slider.valueChanged.connect(lambda x: self.resize(x, x))
        self.tools_layout.addWidget(self.resize_slider)

        self.setMinimumSize(1200, 800)

        self.show()

    def closeEvent(self, ev):
        self.core.shutdown()

    def is_accept_events(self):
        return self.core.is_accept_events()

    def resize(self, w, h):
        self.core.resize(w, h)
        self.updateBoards()

    def update_engine_controls(self):
        self.engine_controls[0].resetSelector(self.core.engine_configs.long_names(), self.core.get_engine_id(0)
                                              , lambda id: self.core.select_engine(0, id))
        self.engine_controls[1].resetSelector(self.core.engine_configs.long_names(), self.core.get_engine_id(1)
                                              , lambda id: self.core.select_engine(1, id))

    def update_game_controls(self):
        self.game_controls[0].resetSelector(self.core.games_db.names()
                                            , lambda id: self.load_game(0, id))
        self.game_controls[1].resetSelector(self.core.games_db.names()
                                            , lambda id: self.load_game(1, id))

    def load_game(self, slot_id, game_id):
        self.core.load_game(slot_id, game_id)
        self.board_widgets[slot_id].update()

    def updateBoards(self):
        self.board_widgets[0].update()
        self.board_widgets[1].update()

    def getBoardWidget(self, id):
        return self.board_widgets[id]

    def getEngineControl(self, id):
        return self.engine_controls[id]

    def print(self, id, text):
        self.consoles[id].print(text)

    def keyPressEvent(self, event):
        if not self.is_accept_events():
            return

        self.board_widgets[0].ignorefocus_keyPressEvent(event)  #TODO: спроектировать красиво
        self.board_widgets[1].ignorefocus_keyPressEvent(event)

        if event.key() == Qt.Key_R:
            self.core.reload_engines()
        if event.key() == Qt.Key_E:
            self.core.add_user_engine("Unknown")
            self.update_engine_controls()
        if event.key() == Qt.Key_X:
            e0 = self.core.get_engine_id(0)
            e1 = self.core.get_engine_id(1)
            self.engine_controls[0].selectEngine(e1)
            self.engine_controls[1].selectEngine(e0)
            self.core.reload_engines()