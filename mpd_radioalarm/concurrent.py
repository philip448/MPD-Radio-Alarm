from tornado.concurrent import Future
from multiprocessing.pool import ThreadPool
from tornado.gen import coroutine

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



