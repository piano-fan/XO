
class BadTurnValue(BaseException):
    ...

class InvalidSquare(BaseException):
    ...

class SquareOccupied(BaseException):
    ...

class SquareEmpty(BaseException):
    ...

class EmptyMovelist(BaseException):
    ...


class Field:
    def __init__(self):
        self.__squares = None
        self.width = None
        self.height = None

    def new(self):
        self.__squares = [[False for x in range(0, self.width)] for y in range(0, self.height)]

    def resize(self, w, h):
        self.width = w
        self.height = h
        self.new()

    def valid_square(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def square_count(self):
        return self.width * self.height

    def place(self, piece, x, y):
        if self.piece(x, y):
            raise SquareOccupied
        self.__squares[y][x] = piece

    def remove(self, x, y):
        if not self.piece(x, y):
            raise SquareEmpty
        self.__squares[y][x] = False

    def piece(self, x, y):
        if not self.valid_square(x, y):
            raise InvalidSquare
        return self.__squares[y][x]

    def trace(self, x, y, turn, dx, dy):
        x1, y1 = x, y
        x2, y2 = x, y
        count = 0
        for i in range(0, 4):
            x1 += dx
            y1 += dy
            if self.valid_square(x1, y1) and self.piece(x1, y1) == turn:
                count += 1
            else:
                break
        for j in range(0, 4):
            x2 -= dx
            y2 -= dy
            if self.valid_square(x2, y2) and self.piece(x2, y2) == turn:
                count += 1
            else:
                break
        return count


class MoveList:
    def __init__(self):
        self.moves = []

    def __iter__(self):
        return self.moves.__iter__()

    def __getitem__(self, key):
        return self.moves[key]

    def append(self, x, y, side):
        self.moves.append((x, y, side))

    def pop(self):
        return self.moves.pop()

    def count(self):
        return len(self.moves)

    def string(self):
        return " ".join([str(x) + ' ' + str(y) for x,y,side in self.moves])


class Game:
    def __init__(self):
        self.field = Field()
        self.moves = False
        self.turn = False
        self.gameover = False

    def new(self):
        self.field.new()
        self.moves = MoveList()
        self.turn = "X"
        self.gameover = False

    def resize(self, w, h):
        self.field.resize(w, h)
        self.moves = MoveList()
        self.turn = "X"
        self.gameover = False

    def make_copy(self, movecount=None):
        result = Game()
        result.resize(self.field.width, self.field.height)
        if movecount is not None:
            for i in range(0, movecount):
                x, y, p = self.moves[i]
                result.move(x, y)
        else:
            for x, y, p in self.moves:
                result.move(x, y)
        return result

    def load(self, other_game):
        self.resize(other_game.field.width, other_game.field.height)
        for x, y, p in other_game.moves:
            self.move(x, y)

    def turn_id(self):
        if self.turn == "X":
            return 0
        elif self.turn == "O":
            return 1
        else:
            raise BadTurnValue

    def swap_turn(self):
        if self.turn == "X":
            self.turn = "O"
        elif self.turn == "O":
            self.turn = "X"
        else:
            raise BadTurnValue

    def check_win(self, x, y):
        turn = self.field.piece(x, y) or self.turn
        for dx, dy in [(1, 0), (1, 1), (0, 1), (-1, 1)]:
            if self.field.trace(x, y, turn, dx, dy) >= 4:
                return True
        return False

    def is_over(self):
        return self.gameover

    def can_move(self, x, y):
        return self.field.valid_square(x, y) and not self.field.piece(x, y) and not self.is_over()

    def can_takeback(self):
        return self.moves.count() > 0

    def move(self, x, y):
        self.field.place(self.turn, x, y)
        self.moves.append(x, y, self.turn)
        self.swap_turn()
        if self.check_win(x, y) or self.moves.count() >= self.field.square_count():
            self.gameover = True

    def takeback(self):
        if self.moves.count() <= 0:
            raise EmptyMovelist
        self.swap_turn()
        x, y, side = self.moves.pop()
        self.field.remove(x, y)
        self.gameover = False

        return x, y, side


class GameObserver():
    def __init__(self):
        self.game = None
        self.__tmp_game = None
        self.__highlights = None

    def bind(self, game):
        self.game = game

    def reset(self):
        self.__tmp_game = self.game.make_copy()
        self.__highlights = Field()
        self.__highlights.resize(self.game.field.width, self.game.field.height)

    def clear_highlights(self):
        self.__highlights.new()

    def highlight_movelist(self, list):
        i = 1
        for x, y, p in list:
            self.__highlights.place(i, x, y)
            i += 1

    def highlight_remaining_moves(self):
        self.clear_highlights()
        self.highlight_movelist(self.game.moves[self.__tmp_game.moves.count(): self.game.moves.count()])

    def forward(self):
        if self.__tmp_game.moves.count() < self.game.moves.count():
            x, y, p = self.game.moves[self.__tmp_game.moves.count()]
            self.__tmp_game.move(x, y)
        self.highlight_remaining_moves()

    def backward(self):
        if self.__tmp_game.moves.count() > 0:
            self.__tmp_game.takeback()
        self.highlight_remaining_moves()

    def get_field(self):
        return self.__tmp_game.field

    def get_highlights(self):
        return self.__highlights
