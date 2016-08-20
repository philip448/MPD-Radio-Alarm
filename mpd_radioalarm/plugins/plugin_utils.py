from mpd_radioalarm.plugins import PluginBase

class UtilsPlugin(PluginBase):
    def initialize(self):
        self.server.add_command('echo', lambda socket, response: response)
