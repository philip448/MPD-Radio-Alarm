from mpd import MPDClient
from mpd import ConnectionError
from time import sleep
from threading import Thread
from playhouse.shortcuts import model_to_dict

from mpd_radioalarm.plugins import PluginBase
from .handler import ManageMediaHandler, PlayHandler
from . import model

MAX_RECONNECT = 10


class MPDPlugin(PluginBase):
    def initialize(self):
        self.mpd_client = MPDClient()
        self.playlist = []

        self._initialize_commands()
        self._initialize_topics()
        self._initialize_handlers()
        self._initialize_models()
        self._initialize_mpd_client()

        ManageMediaHandler.playlist_changed.addHandler(self.reload_playlist)

    def _initialize_mpd_client(self):
        try:
            self.mpd_client.timeout = 10
            self.mpd_client.idletimeout = None
            self.mpd_client.connect(self.config.MPD_HOST, self.config.MPD_PORT)
            self.reload_playlist()
            self._start_periodic_song_updates()


        except ConnectionRefusedError:
            print('Connection to MPD Failed. Retrying in 10 secs. ')

            def retry():
                sleep(10)
                self._initialize_mpd_client()

            t = Thread(target=retry)
            t.start()

    def _initialize_models(self):
        self.model.create_table(model.BroadcastTransmitter)
        self.model.create_table(model.Alarm)
        self.model.create_table(model.MP3File)

    def _initialize_commands(self):
        self.server.add_command('mpd.play', lambda socket: self._song_command(self.mpd_client.play))
        self.server.add_command('mpd.pause', lambda socket: self._song_command(self.mpd_client.pause))
        self.server.add_command('mpd.next', lambda socket: self._song_command(self.mpd_client.next))
        self.server.add_command('mpd.previous', lambda socket: self._song_command(self.mpd_client.previous))
        self.server.add_command('mpd.stop', lambda socket: self._song_command(self.mpd_client.stop))

        self.server.add_command('mpd.currentsong', lambda socket: self._try_action(self.mpd_client.currentsong))
        self.server.add_command('mpd.playlist', lambda socket: self.playlist)
        self.server.add_command('mpd.status', lambda socket: self._try_action(self.mpd_client.status))

    def _initialize_topics(self):
        self.server.add_topic('mpd.currentsong')
        self.server.add_topic('mpd.status')
        self.server.add_topic('mpd.playlist')

    def _initialize_handlers(self):
        self.server.add_handler(r'/manage-media', ManageMediaHandler)
        self.server.add_handler(r'/play', PlayHandler)

    def _start_periodic_song_updates(self):
        t = Thread(target=self._t_update_topics)
        t.start()

    def _t_update_topics(self):
        while True:
            self.server.update_topic('mpd.currentsong', self.mpd_client.currentsong())
            sleep(5)

    def _try_action(self, action, approach=1, args=()):
        try:
            val = action(*args)
            return val
        except ConnectionError as ex:
            self.mpd_client.connect(self.config.MPD_HOST, self.config.MPD_PORT)
            if (approach < MAX_RECONNECT):
                return self._try_action(action, approach + 1)
            else:
                raise ex

    def _song_command(self, action, args=()):
        result = self._try_action(action, args=args)
        status = self._try_action(self.mpd_client.status)
        self.server.update_topic('mpd.status', status)
        self.server.update_topic('mpd.currentsong', self._try_action(self.mpd_client.currentsong))
        return result

    def reload_playlist(self):
        mpd_status = self.mpd_client.status()
        status_index = mpd_status.get('song')
        status_state = mpd_status['state']

        self.mpd_client.clear()

        for i in model.BroadcastTransmitter.select():
            self.mpd_client.add(i.url)
            self.playlist.append(model_to_dict(i))

        if status_state == 'play':
            self._song_command(self.mpd_client.play, args=(status_index,))
