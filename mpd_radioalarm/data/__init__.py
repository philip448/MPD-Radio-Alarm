from tornado.concurrent import Future
from threading import Thread
import hashlib

from mpd_radioalarm import config


def in_thread(action):
    f = Future()

    def wrapper():
        try:
            r = action()

            f.set_result(r)
        except Exception as ex:
            f.set_exception(ex)

    t = Thread(target=wrapper)
    t.start()

    return f


def password(plain):
    if not config.HASH_PASSWORD:
        return plain

    return str(hashlib.pbkdf2_hmac(config.HASH_ALGO, str.encode(plain), str.encode(config.HASH_SALT), config.HASH_ITERATIONS))