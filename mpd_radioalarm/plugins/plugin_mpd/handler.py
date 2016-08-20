from mpd_radioalarm.plugins import PluginBase
from mpd_radioalarm import EventHook

from .model import *


class ManageMediaHandler(PluginBase.handler.BaseHandler):
    playlist_changed = EventHook()

    @PluginBase.concurrent.coroutine
    def get(self):

        @PluginBase.concurrent.in_thread
        def receive_data():
            return BroadcastTransmitter.select()

        bts = yield receive_data()
        self.render('manage-media/index.html', broadcast_transmitters=bts)

    @PluginBase.concurrent.coroutine
    def post(self):
        action = self.get_argument('action')
        name = self.get_argument('name')

        @PluginBase.concurrent.in_thread
        def update_data():
            if action == 'add':
                url = self.get_argument('url')
                bt = BroadcastTransmitter.create(url=url, name=name)
                bt.save()
            elif action == 'delete':
                bt = BroadcastTransmitter.get(name=name)
                bt.delete_instance()

        yield update_data()
        self.playlist_changed.fire()
        self.redirect('manage-media')


class PlayHandler(PluginBase.handler.BaseHandler):
    def get(self):
        self.render('play.html')

