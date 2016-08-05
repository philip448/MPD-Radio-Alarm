from mpd_radioalarm.websocket import add_command


def initialize():
    add_command('echo', lambda socket, response: response)
