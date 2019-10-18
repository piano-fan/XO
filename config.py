import configparser


class Config:
    class Base:
        def __init__(self, filename):
            assert type(filename) == str
            self.filename = filename
            self.device = configparser.ConfigParser()
            self.device.read(filename)

        def save(self):
            with open(self.filename, 'w') as configfile:
                self.device.write(configfile)

        def list(self): #slow
            result = [item for item in self.device.__iter__()]
            result.remove("DEFAULT")
            return result

        def __iter__(self):
            return self.list().__iter__()

        def __getitem__(self, section):
            assert type(section) == str
            assert section != "DEFAULT"
            return self.device[section]

        def __setitem__(self, section, value):
            assert type(section) == str
            assert section != "DEFAULT"
            self.device[section] = value

        def __delitem__(self, section):
            assert type(section) == str
            assert section != "DEFAULT"
            self.device[section] = None

        def __contains__(self, section):
            assert type(section) == str
            assert section != "DEFAULT"
            return section in self.device


    class Engines(Base):
        def __init__(self, filename):
            Config.Base.__init__(self, filename)

        def make_unique_id(self):   #slow but simple
            for id in range(1000):
                if not id in self:
                    return id
            else:
                raise Config.BadSection

        def names(self):
            return [self[id]["name"] for id in range(self.count())]

        def long_names(self):
            return [self[id]["name"] + " (" + self[id]["path"] + ")" for id in range(self.count())]

        def add(self, name, path, need_local_copy=False):
            id = self.make_unique_id()
            self[id] = {"name": name, "path": path, "need_local_copy": need_local_copy}
            return id

        #def remove(self, id):   #в данном исполнении будет провоцировать ошибки
        #    assert id in self
        #    self[id] = None

        def count(self):    #slow
            return len(self.list())

        def __getitem__(self, id):
            assert type(id) == int
            return self.device[str(id)]

        def __setitem__(self, id, value):
            assert type(id) == int
            self.device[str(id)] = value

        def __delitem__(self, id):
            assert type(id) == int
            self.device[str(id)] = None

        def __contains__(self, id):
            assert type(id) == int
            return str(id) in self.device