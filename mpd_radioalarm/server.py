from tornado.web import Application
from tornado.ioloop import IOLoop
from peewee import DoesNotExist

from mpd_radioalarm import config
from mpd_radioalarm.handler import *
from mpd_radioalarm.data.model import User
from mpd_radioalarm.data import password
from mpd_radioalarm.websocket import WebSocketHandler
from mpd_radioalarm.plugins import import_plugins


def create_root_user():
    try:
        u = User.get(email=config.ROOT_USER_EMAIL)
        return u
    except DoesNotExist:
        pass

    u = User.create(email=config.ROOT_USER_EMAIL, password=password(config.ROOT_USER_PASSWORD))
    u.save()


def make_app():

    create_root_user()
    app = Application(
        [
            (r'/', WebHandler),
            (r'/login', LoginHandler),
            (r'/play', PlayHandler),
            (r'/ws', WebSocketHandler),
            (r'/manage-media', ManageMediaHandler)
        ],
        static_path=config.STATIC_FILE_PATH,
        template_path=config.TEMPLATE_PATH,
        debug=config.DEBUG,
        cookie_secret=config.COOKIE_SECRET
    )

    return app

if __name__ == '__main__':
    app = make_app()
    app.listen(config.HTTP_PORT)
    IOLoop.current().start()