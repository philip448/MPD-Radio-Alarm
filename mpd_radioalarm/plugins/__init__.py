import importlib
import inspect
import os

from mpd_radioalarm import handler
from mpd_radioalarm import model
from mpd_radioalarm import password
from mpd_radioalarm import concurrent
from mpd_radioalarm import config


def import_plugins(server):
    for module in os.listdir(os.path.dirname(__file__)):
        if module == '__init__.py':
            continue
        if module[-3:] == '.py':
            plugin = importlib.import_module("mpd_radioalarm.plugins.{}".format(module[:-3]))
        else:
            plugin = importlib.import_module("mpd_radioalarm.plugins.{}".format(module))

        for i in inspect.getmembers(plugin):
            if inspect.isclass(i[1]) and issubclass(i[1], PluginBase) and i[1].__name__ != PluginBase.__name__:

                print(i[1].__name__)
                p = i[1](server)
                p.initialize()
                print('Plguin initialized')


class PluginBase(object):
    handler = handler
    model = model
    concurrent = concurrent
    config = config

    def hash_password(self, plain):
        return password(plain)

    def __init__(self, server):
        self.server = server

    def initialize(self):
        raise NotImplementedError('Override initialize')

    def get_information(self):
        raise NotImplementedError('Override get_information')


class PluginInformation(object):
    def __init__(self,
                 name, version, vendor,
                 template_dir):
        self.name = name
        self.version = version
        self.vendor = vendor
        self.template_dir = template_dir

class PluginManager(object):
    def __init__(self):
        pass



