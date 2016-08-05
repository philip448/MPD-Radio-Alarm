from mpd import MPDClient
from mpd import ConnectionError
from time import sleep
from threading import Thread

from mpd_radioalarm.websocket import add_command, update_topic, add_topic
from mpd_radioalarm import config
from mpd_radioalarm.data.model import BroadcastTransmitter


client = MPDClient()

MAX_RECONNECT = 10

def t_update_topics():
    update_topic('mpd.currentsong', client.currentsong())
    sleep(10)


def initialize():
    client.timeout = 10
    client.idletimeout = None
    client.connect(config.MPD_HOST, config.MPD_PORT)

    def try_action(action, approach=1):
        try:
            val = action()
            return val
        except ConnectionError as ex:
            client.connect(config.MPD_HOST, config.MPD_PORT)
            if (approach < MAX_RECONNECT):
                return try_action(action, approach+1)
            else:
                raise ex

    def song_command(action):
        result = try_action(action)
        update_topic('mpd.currentsong', try_action(client.currentsong))
        return result




    client.clear()
    for i in BroadcastTransmitter.select():
        client.add(i.url)

    add_command('mpd.play', lambda socket: song_command(client.play))
    add_command('mpd.pause', lambda socket: song_command(client.pause))
    add_command('mpd.next', lambda socket: client.next())
    add_command('mpd.previous', lambda socket: client.previous())
    add_command('mpd.currsong', lambda socket: try_action(client.currentsong))

    add_command('mpd.status', lambda socket: try_action(client.status))

    add_topic('mpd.currentsong')

    t = Thread(target=t_update_topics)
    t.start()

