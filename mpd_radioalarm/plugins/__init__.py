import os
import importlib
import inspect

from mpd_radioalarm.plugins import plugin_api


def import_plugins(server):
    for module in os.listdir(os.path.dirname(__file__)):
        if module == '__init__.py' or module[-3:] != '.py' or module == 'plugin_api.py':
            continue
        plugin = importlib.import_module("mpd_radioalarm.plugins.{}".format(module[:-3]))
        for i in inspect.getmembers(plugin):
            if inspect.isclass(i[1]) and issubclass(i[1], PluginBase) and i[1].__name__ != PluginBase.__name__:

                print(i[1].__name__)
                p = i[1](server)
                p.initialize()
                print('Plguin initialized')


class PluginBase(object):
    def __init__(self, server):
        self.server = server
        self.plugin_api = plugin_api

    def initialize(self):
        raise NotImplementedError('Override initialize')

