from tornado.ioloop import IOLoop
from tornado.web import Application

from model import User
from mpd_radioalarm import websocket
from mpd_radioalarm import password
from mpd_radioalarm.handler import *


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
        rpc_server = websocket.RPCServer()
        super().__init__([
            (r'/', WebHandler),
            (r'/login', LoginHandler),
            (r'/admin', AdminHandler),
            (r'/admin/user', AdminUserHandler),
            (r'/ws', websocket.WebSocketHandler, dict(rpc_server=rpc_server))
        ],
            static_path=config.STATIC_FILE_PATH,
            template_path=config.TEMPLATE_PATH,
            debug=config.DEBUG,
            cookie_secret=config.COOKIE_SECRET)

        # Wrap methods for access
        self.add_command = rpc_server.add_command
        self.remove_command = rpc_server.remove_command
        self.add_topic = rpc_server.add_topic
        self.remove_topic = rpc_server.remove_topic
        self.update_topic = rpc_server.update_topic

    def start(self, port=config.HTTP_PORT):
        self.listen(port)
        IOLoop.current().start()

    def add_handler(self, url, handler):
        self.add_handlers(r'.*', [(url, handler)])
