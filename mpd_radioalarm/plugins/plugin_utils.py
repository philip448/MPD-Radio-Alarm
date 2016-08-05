from websocket import add_command

PLUGIN_NAME_UTILS = None

def initialize():
    add_command('echo', lambda response: response)
