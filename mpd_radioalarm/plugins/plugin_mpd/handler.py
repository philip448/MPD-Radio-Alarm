from mpd_radioalarm.plugins import plugin_api
from mpd_radioalarm.data.model import BroadcastTransmitter


class ManageMediaHandler(plugin_api.BaseHandler):
    @plugin_api.coroutine
    def get(self):

        @plugin_api.in_thread
        def receive_data():
            return BroadcastTransmitter.select()

        bts = yield receive_data()
        self.render('manage-media/index.html', broadcast_transmitters=bts)

    @plugin_api.coroutine
    def post(self):
        action = self.get_argument('action')
        name = self.get_argument('name')

        @plugin_api.in_thread
        def update_data():
            if action == 'add':
                url = self.get_argument('url')
                bt = BroadcastTransmitter.create(url=url, name=name)
                bt.save()
            elif action == 'delete':
                bt = BroadcastTransmitter.get(name=name)
                bt.delete_instance()

        yield update_data()

        self.redirect('manage-media')

class PlayHandler(plugin_api.BaseHandler):
    def get(self):
        self.render('play.html')

