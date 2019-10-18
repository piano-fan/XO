from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import math

from game import *


class QBoardWidget(QWidget):
    def __init__(self, parent, slot_id):
        super().__init__(parent)
        self.__slot_id = slot_id
        self.setFocusPolicy(Qt.StrongFocus)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumSize(500, 500)
        self.game_observer = GameObserver()
        self.update_observer()

    def is_accept_events(self):
        return self.parent().is_accept_events()

    def get_engine_manager(self):
        return self.parent().core.engine_manager

    def update_observer(self):
        game = self.parent().core.games[self.__slot_id]
        self.game_observer.bind(game)
        self.update()

    def squareSize(self):
        w = self.width() / self.game_observer.get_field().width * .9
        h = self.height() / self.game_observer.get_field().height * .9
        return QSize(w, h)

    def fieldBorderSize(self):
        w = self.width() / 20
        h = self.height() / 20
        return QSize(w, h)

    def squareBorderSize(self):
        return self.squareSize() / 10

    def cursorXYToSquareXY(self, x, y):
        return (math.floor((x - self.fieldBorderSize().width()) / self.squareSize().width()),
                math.floor((y - self.fieldBorderSize().height()) / self.squareSize().height()))

    def paintEvent(self, event):
        if not self.game_observer:
            return

        painter = QPainter(self)
        sq_w, sq_h = self.squareSize().width(), self.squareSize().height()
        field_border_w, field_border_h = self.fieldBorderSize().width(), self.fieldBorderSize().height()
        sq_border_w, sq_border_h = self.squareBorderSize().width(), self.squareBorderSize().height()

        for x in range(0, self.game_observer.get_field().width):
            cx = x * sq_w + field_border_w
            for y in range(0, self.game_observer.get_field().height):
                cy = y * sq_h + field_border_h
                shape = self.game_observer.get_field().piece(x, y)
                if shape == "X":
                    painter.drawLine(cx + sq_border_w, cy + sq_border_h,
                                     cx + sq_w - sq_border_w, cy + sq_h - sq_border_h)
                    painter.drawLine(cx + sq_w - sq_border_w, cy + sq_border_h,
                                     cx + sq_border_w, cy + sq_h - sq_border_h)
                elif shape == "O":
                    painter.drawEllipse(cx + sq_border_w, cy + sq_border_h, sq_w * .8, sq_h * .8)

                else:
                    highlight = self.game_observer.get_highlights().piece(x, y)
                    if type(highlight) == int:
                        painter.drawText(cx, cy, sq_w, sq_h, Qt.AlignVCenter | Qt.AlignHCenter, str(highlight))


                painter.drawRect(cx, cy, sq_w, sq_h)

        for i in range(0, self.game_observer.get_field().width):
            cx = i * sq_w + field_border_w
            painter.drawText(cx, 0, sq_w, field_border_h, Qt.AlignVCenter | Qt.AlignHCenter, str(i))
        for i in range(0, self.game_observer.get_field().height):
            cy = i * sq_h + field_border_h
            painter.drawText(0, cy, field_border_w, sq_h, Qt.AlignVCenter | Qt.AlignHCenter, str(i))


    def wheelEvent(self, event):
        if not self.game_observer:
            return

        if event.angleDelta().y() < 0:
            self.game_observer.backward()
        else:
            self.game_observer.forward()
        super().update()

    def mousePressEvent(self, event):
        if not self.game_observer:
            return
        if not self.is_accept_events():
            return

        if event.button() == Qt.LeftButton:
            x, y = self.cursorXYToSquareXY(event.x(), event.y())
            if self.game_observer.game.can_move(x, y):
                self.game_observer.game.move(x, y)
                self.update()
        elif event.button() == Qt.RightButton:
            if self.game_observer.game.can_takeback():
                self.game_observer.game.takeback()
                self.update()

    def ignorefocus_keyPressEvent(self, event):
        if not self.underMouse():
            return
        if not self.is_accept_events():
            return
        mouse = self.mapFromGlobal(QCursor.pos())
        x, y = self.cursorXYToSquareXY(mouse.x(), mouse.y())

        if event.key() == Qt.Key_N:
            self.parent().core.new_game(self.__slot_id)
            self.update()
        if event.key() == Qt.Key_I:
            if self.game_observer.game.field.valid_square(x, y):
                self.get_engine_manager().print_square_info(self.__slot_id
                                                        , self.game_observer.game, x, y)
        if event.key() == Qt.Key_Q:
            if not self.game_observer.game.is_over():
                if event.modifiers() & Qt.ShiftModifier:
                    self.get_engine_manager().single_play(self.__slot_id)
                    self.update()
                else:
                    self.get_engine_manager().think(self.__slot_id)
                    self.update()

        if event.key() == Qt.Key_W:
            self.parent().core.engine_manager.dual_play(self.__slot_id)
            self.update()
        if event.key() == Qt.Key_S:
            self.parent().core.save_game(self.__slot_id)
            self.parent().update_game_controls()

    def update(self):
        self.game_observer.reset()
        super().update()

