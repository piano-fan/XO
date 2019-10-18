import os
import pickle


class Games_DB():
    def __init__(self, dir='db'):
        self.dir = dir
        if not os.path.isdir(dir):
            os.makedirs(dir)
        self.games = []
        for _, _, names in os.walk(dir):
            for file in names:
                nextpath = os.path.join(dir, file)
                self.__append(file, pickle.load(open(nextpath, "rb")))
            break
        self.games.sort(key=self.__record_key)

    def __record_key(self, record):
        return record["name"]

    def __append(self, name, game):
        self.games.append({
            "data" : game,
            "name" : name
        })

    def append(self, name, game):
        self.__append(name, game.make_copy())
        pickle.dump(game, open(os.path.join(self.dir, name), "wb"))

    def names(self):
        return [record["name"] for record in self.games]