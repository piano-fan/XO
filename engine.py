import threading
import re
import os
from shutil import copy

from BrainDaemon.main import Brain


from PyQt5.QtCore import pyqtSignal, QObject


class EngineCrashed(BaseException):
    ...


class XOLock:
    def __init__(self):
        self.__lock = threading.Lock()

    def locked(self):
        can_acquire = self.__lock.acquire(False)
        if can_acquire:
            self.__lock.release()
            return False
        return True

    def acquire(self):
        self.__lock.acquire()

    def release(self):
        self.__lock.release()

    def wait(self):
        self.__lock.acquire()
        self.__lock.release()


class EngineController(QObject):
    con_print = pyqtSignal('QString')

    def __init__(self, slot_id):
        super().__init__()
        self.__slot_id = slot_id
        self.__device = None
        self.info = None
        self.__lock = XOLock()
        self.__show_engine_io = 0
        
    def __make_engine_prompt(self):
        prompt = '[' + str(self.__slot_id) + ']'
        if 'name' in self.info:
            prompt += self.info['name']
            if 'version' in self.info:
                prompt += ' ' + self.info['version']
            if 'author' in self.info:
                prompt += ' by ' + self.info['author']

        return prompt

    def ready(self):
        return self.__device is not None \
            and self.__device.exit_code() is None

    def set_show_engine_io(self, value):
        self.__show_engine_io = value

    def locked(self):
        return self.__lock.locked()

    def send_command(self, text):
        if not self.ready():
            print('engine[' + str(self.__slot_id) + '] ERROR: device is not ready for command ' + text)
            return
        self.on_engine_input(text)
        self.__lock.acquire()
        self.__device.send_message(text)
        self.__lock.wait()
        code = self.__device.exit_code()
        if code:
            print('engine[' + str(self.__slot_id) + '] ERROR: device crashed after command ' + text)
            raise EngineCrashed

    def start(self, properties):
        self.info = {}

        exec_path = None
        if properties["need_local_copy"]:
            exec_path = "./engine" + str(self.__slot_id)
            copy(properties["path"], exec_path)
        else:
            exec_path = properties["path"]

        self.__device = Brain(exec_path
             , on_stdout=lambda text: self.on_engine_output(text)
             , on_stderr=lambda text: print('engine[' + str(self.__slot_id) + '] ' + text)
             , on_shutdown=lambda code: self.on_engine_shutdown(code))

        self.call_about()

    def shutdown(self):
        if self.__device:
            self.__device.shutdown()

    def kill(self):
        if self.__device:
            self.__device.kill()

    def call_about(self):
        self.send_command('about')
        pattern = '\s*(\w+)\s*=\s*"([^"]+)"\s*,?\s*'
        pairs = re.findall(pattern, self.last_text)
        if len(pairs) > 0:
            for key, value in pairs:
                self.info[key] = value
        elif self.last_command == 'unknown':
            ...
        else:
            ...  # TODO: raise

    def new_game(self, w, h):
        self.send_command('start ' + str(w) + ' ' + str(h))
        if self.last_command == 'ok':
            return
        elif self.last_command == 'error':
            ...   #TODO:
        else:
            ...  # TODO: what?

    def think(self, game):
        self.new_game(game.field.width, game.field.height)
        if game.moves.count() == 0:
            self.send_command("begin")
        else:
            self.load_game(game)
        x, y = self.last_command.split(',')
        game.move(int(x), int(y))

    def play(self, game):
        self.new_game(game.field.width, game.field.height)
        self.load_game(game, False)
        self.send_command('single_play')

        if self.last_command == 'play' and len(self.last_args) > 1:
            moves = self.last_args[1].rstrip().split(' ')
            while len(moves) > 0:
                x = int(moves.pop(0))
                y = int(moves.pop(0))
                try:
                    game.move(x, y)
                except:
                    print("ERROR: square occupied " + str(x) + "," + str(y))
        elif self.last_command == 'unknown':
            print("Single play is not supported by engine " + str(self.__slot_id))
        else:
            ...  # ???
        return

    def load_game(self, game, want_best_move=True):
        if game.moves.count() == 0:
            return
        text = 'board\n'
        side_id = game.turn_id() + 1

        for i in range(0, game.moves.count()):
            move = game.moves[i]
            text += '' + str(move[0]) + ',' + str(move[1]) + ',' + str(side_id) + '\n'
            side_id = side_id % 2 + 1

        if want_best_move:
            text += 'done'
        else:
            text += 'load'
        self.send_command(text)

    def print_square_info(self, game, x, y):
        self.new_game(game.field.width, game.field.height)
        self.load_game(game, False)
        self.send_command("squareinfo " + str(x) + " " + str(y))

    def on_engine_input(self, text):
        if self.__show_engine_io:
            output_text = self.__make_engine_prompt()
            output_text += ' <<< '
            output_text += text
            self.con_print.emit(output_text)

    def on_engine_message(self, message):
        self.con_print.emit(self.__make_engine_prompt() + ': ' + message)

    def on_engine_output(self, text):
        self.last_text = text
        self.last_args = text.rstrip().split(' ', 1)
        self.last_command = self.last_args[0].lower().rstrip()

        if self.last_command == 'message':
            msg = ''
            if len(self.last_args) > 1:
                msg += self.last_args[1]
                self.on_engine_message(msg)
            return

        output_text = self.__make_engine_prompt()

        if self.__show_engine_io:
            output_text += ' >>> ' + text
            self.con_print.emit(output_text)

        if self.__lock.locked():
            self.__lock.release()
            return

        else:
            ... #TODO: what is it

    def on_engine_shutdown(self, code):
        print('engine[' + str(self.__slot_id) + '] finished with exit code ' + str(code))
        if code != 0 and self.__lock.locked():
            self.__lock.release()



class EngineBinding:
    class Base:
        def __init__(self):
            raise NotImplementedError

        def think(self):
            raise NotImplementedError

        def play(self):
            raise NotImplementedError

        def ready(self):
            raise NotImplementedError

    class SingleEngine(Base):
        def __init__(self, engine, game):
            self.__engine = engine
            self.__game = game

        def think(self):
            self.__engine.think(self.__game)

        def play(self):
            self.__engine.play(self.__game)

        def ready(self):
            return self.__engine.ready()

    class DualEngine(Base):
        def __init__(self, engine0, engine1, game):
            self.__engines = []
            self.__engines.append(engine0)
            self.__engines.append(engine1)
            self.__game = game

        def think(self):
            if not self.__game.is_over():
                if self.__game.turn == 'X':
                    self.__engines[0].think(self.__game)
                elif self.__game.turn == 'O':
                    self.__engines[1].think(self.__game)
                else:
                    assert(False)

        def play(self):
            while not self.__game.is_over():
                self.think()

        def ready(self):
            return self.__engines[0].ready() and self.__engines[1].ready()

    class DualGame(Base):
        def __init__(self, engine0, engine1, game0, game1):
            self.__bind0 = EngineBinding.SingleEngine(engine0, game0)
            self.__bind1 = EngineBinding.SingleEngine(engine1, game1)

        def think(self):
            self.__bind0.think()
            self.__bind1.think()

        def play(self):
            self.__bind0.play()
            self.__bind1.play()

        def ready(self):
            return self.__bind0.ready() and self.__bind1.ready()


class EngineManager:
    def __init__(self, core):
        self.__core = core
        self.__engines = [EngineController(0), EngineController(1)]

    def get_engine_properties(self, id):
        return self.__core.engine_configs[id]

    def get_controller(self, slot_id):
        return self.__engines[slot_id]

    def __run_engine(self, slot_id, engine_id): #TODO FIX: добавляет в неизвестный индекс
        self.__engines[slot_id].set_show_engine_io(self.__core.get_show_engine_io(slot_id))
        try:
            self.__engines[slot_id].start(self.get_engine_properties(engine_id))
        except EngineCrashed:
            ...

    def run_engines(self):
        try:
            self.__run_engine(0, self.__core.get_engine_id(0))
            self.__run_engine(1, self.__core.get_engine_id(1))
        except EngineCrashed:
            ...

    def shutdown(self):
        for engine in self.__engines:
            if engine.ready():
                engine.shutdown()

    def single_play(self, slot_id):
        delegate = EngineBinding.SingleEngine(self.__engines[slot_id], self.__core.games[slot_id])
        try:
            if delegate.ready():
                delegate.play()
        except EngineCrashed:
            ...

    def dual_play(self, slot_id):
        if slot_id == 0:
            delegate = EngineBinding.DualEngine(self.__engines[0], self.__engines[1], self.__core.games[0])
        elif slot_id == 1:
            delegate = EngineBinding.DualEngine(self.__engines[1], self.__engines[0], self.__core.games[1])
        else:
            assert(False)

        try:
            if delegate.ready():
                delegate.think()
        except EngineCrashed:
            ...

    def think(self, slot_id=None):
        if slot_id is None:
            delegate = EngineBinding.DualGame(self.__engines[0], self.__engines[1]
                                          , self.__core.games[0], self.__core.games[1])
        else:
            delegate = EngineBinding.SingleEngine(self.__engines[slot_id], self.__core.games[slot_id])
        try:
            if delegate.ready():
                delegate.think()
        except EngineCrashed:
            ...

    def is_locked(self):
        for engine in self.__engines:
            if engine.locked():
                return True
        return False

    def print_square_info(self, slot_id, game, x, y):
        try:
            if self.__engines[slot_id].ready():
                self.__engines[slot_id].print_square_info(game, x, y)
        except EngineCrashed:
            ...
