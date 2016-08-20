from tornado.web import Application
from tornado.ioloop import IOLoop
from peewee import DoesNotExist

from mpd_radioalarm import config
from mpd_radioalarm.handler import *
from mpd_radioalarm.data.model import User
from mpd_radioalarm.data import password
from mpd_radioalarm import websocket


def create_root_user():
    try:
        u = User.get(email=config.ROOT_USER_EMAIL)
        return u
    except DoesNotExist:
        pass

    u = User.create(email=config.ROOT_USER_EMAIL, password=password(config.ROOT_USER_PASSWORD))
    u.save()


class Server(Application):
    def __init__(self):
        create_root_user()
        super().__init__([
            (r'/', WebHandler),
            (r'/login', LoginHandler),
            (r'/ws', websocket.WebSocketHandler)
        ],
            static_path=config.STATIC_FILE_PATH,
            template_path=config.TEMPLATE_PATH,
            debug=config.DEBUG,
            cookie_secret=config.COOKIE_SECRET)

    def add_handler(self, url, handler):
        self.add_handlers(r'.*', [(url, handler)])

    def update_topic(self, topic, update):
        websocket.update_topic(topic, update)

    def add_topic(self, topic):
        websocket.add_topic(topic)

    def add_command(self, name, func):
        websocket.add_command(name, func)

    def start(self, port=config.HTTP_PORT):
        self.listen(port)
        IOLoop.current().start()
