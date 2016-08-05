import os
import importlib

def import_plugins():
    for module in os.listdir(os.path.dirname(__file__)):
        if module == '__init__.py' or module[-3:] != '.py':
            continue
        plugin = importlib.import_module("mpd_radioalarm.plugins.{}".format(module[:-3]))
        plugin.initialize()
