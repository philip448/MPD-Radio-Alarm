from tornado.concurrent import Future
from threading import Thread
import hashlib

from mpd_radioalarm import config
from multiprocessing.pool import ThreadPool
from tornado.ioloop import IOLoop

MAX_WORKERS = 10
_workers = ThreadPool(MAX_WORKERS)


def in_thread(action):
    def wrap(*args, **kwargs):
        f = Future()

        def _callback(result):
            f.set_result(result)

        def _error_callback(error):
            f.set_exception(error)

        _workers.apply_async(action, args, kwargs, _callback, _error_callback)
        return f

    return wrap


def password(plain):
    if not config.HASH_PASSWORD:
        return plain

    return str(hashlib.pbkdf2_hmac(config.HASH_ALGO, str.encode(plain), str.encode(config.HASH_SALT), config.HASH_ITERATIONS))
