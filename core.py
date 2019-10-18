from config import Config
from game import *
from engine import EngineManager
from CoreWidget import QCoreWidget
from PyQt5.QtWidgets import QFileDialog, QInputDialog
import pickle
from games_db import Games_DB


class XOCore():
    def __init__(self):
        self.loaded = False
        self.config = Config.Base("core.cfg")

        self.engine_configs = None
        self.init_engine_configs()

        self.games = None
        self.games_db = Games_DB()
        self.init_games()

        self.engine_manager = EngineManager(self)
        self.CoreWidget = QCoreWidget(self)

        self.connect_engines()

        ## TODO: scan Engines folder
        self.engine_manager.run_engines()

        self.loaded = True

    def get_engine_path_from_user(self):
        path = QFileDialog.getOpenFileName(None, 'Select engine', './')[0]
        if path and path == '':
            return None
        return path

    def init_engine_configs(self):
        self.engine_configs = Config.Engines("engines.cfg")
        if self.engine_configs.count() < 1:
            self.engine_configs.add("Default", self.get_engine_path_from_user(), True)
            self.engine_configs.save()

    def add_user_engine(self, name):
        path = self.get_engine_path_from_user();
        if not path:
            return
        self.engine_configs.add(name, path, False)
        self.engine_configs.save()

    def load_game(self, slot_id, game_id):
        self.games[slot_id].load(self.games_db.games[game_id]["data"])

    def save_game(self, slot_id):
        name, ok = QInputDialog.getText(self.CoreWidget, 'Save game', 'Game name:')
        if ok:
            self.games_db.append(name, self.games[slot_id])

    def init_games(self):
        self.games = [Game(), Game()]
        self.games[0].resize(16, 16)
        self.games[1].resize(16, 16)

    def reload_engines(self):
        self.engine_manager.shutdown()
        self.engine_manager = EngineManager(self)
        self.connect_engines()
        self.engine_manager.run_engines()

    def shutdown(self):
        self.engine_manager.shutdown()

    def connect_engines(self):
        self.CoreWidget.getEngineControl(0).attachEngine(self.engine_manager.get_controller(0))
        self.CoreWidget.getEngineControl(1).attachEngine(self.engine_manager.get_controller(1))

    def new_game(self, slot_id):
        self.games[slot_id].new()

    def resize(self, w, h):
        self.games[0].resize(w, h)
        self.games[1].resize(w, h)

    def engine_slot_name(self, slot_id):
        return "engine" + str(slot_id)

    def get_engine_id(self, slot_id):
        try:
            return int(self.config[self.engine_slot_name(slot_id)]["id"])
        except KeyError:
            return 0

    def select_engine(self, slot_id, engine_id):
        if not self.engine_slot_name(slot_id) in self.config:
            self.config[self.engine_slot_name(slot_id)] = {}
        self.config[self.engine_slot_name(slot_id)]["id"] = str(engine_id)
        self.config.save()

    def get_show_engine_io(self, slot_id):
        try:
            return int(self.config[self.engine_slot_name(slot_id)]["show engine io"])
        except KeyError:
            return 0

    def set_show_engine_io(self, slot_id, value):
        if not self.engine_slot_name(slot_id) in self.config:
            self.config[self.engine_slot_name(slot_id)] = {}
        self.config[self.engine_slot_name(slot_id)]["show engine io"] = str(value)
        self.config.save()

    """def load(self, filename='DefaultSave'):
        self.game.load(filename)

    def save(self, filename='DefaultSave'):
        self.game.moves.save(filename)"""

    def is_accept_events(self):
        return self.loaded and not self.engine_manager.is_locked()   #TODO: EM.is_locked broken
