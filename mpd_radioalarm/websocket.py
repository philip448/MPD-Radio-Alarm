from tornado.websocket import WebSocketHandler as TornWebSocketHandler
from tornado.gen import coroutine
import json
import jsonschema

from mpd_radioalarm.handler import BaseHandler as RequestBaseHandler
from mpd_radioalarm.concurrent import in_thread
from mpd_radioalarm import config
from mpd_radioalarm import EventHook

MESSAGE_FORMAT = {
    "type": "object",
    "properties": {
        "type": {
            "type": "string",
            "enum": ["call"]
        },
        "data": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                },
                "arguments": {
                    "type": "object"
                },
                "id": {
                    "type": "string"
                }
            },

            "required": ["command"]
                }
            }
}


class RPCServer(object):
    def __init__(self):
        self._commands = {}
        self._topics = {}

        self.add_command('subscribe', self._subscribe)

    def add_command(self, name, func):
        self._commands[name] = func

    def remove_command(self, name):
        c = self._commands[name]
        del self._commands[name]
        return c

    def add_topic(self, topic):
        self._topics[topic] = []

    def remove_topic(self, topic):
        t = self._topics[topic]
        del self._topics[topic]
        return t

    def update_topic(self, topic, update):
        msg = {
            "type": "update",
            "topic": topic,
            "data": update
        }
        str_msg = json.dumps(msg)

        for sock in self._topics[topic]:
            sock.write_message(str_msg)

    def _subscribe(self, socket, topic):
        socket.on_socket_close.addHandler(lambda: self._topics[topic].remove(socket))
        self._topics[topic].append(socket)
        return {
            'success': True,
            'topic': topic
        }

    def _call_command(self, socket, command, kwargs):
        return self._commands[command](socket, **kwargs)


class WebSocketHandler(TornWebSocketHandler):
    on_socket_close = EventHook()

    def initialize(self, rpc_server):
        RequestBaseHandler.initialize(self)
        self.rpc_server = rpc_server


    @coroutine
    def prepare(self):

        @in_thread
        def get_user():
            return RequestBaseHandler.get_current_user(self)

        user = yield get_user()

        if not user:
            return self.close()

        self.current_user = user

    @coroutine
    def on_message(self, message):
        if config.DEBUG:
            print('in: ' + message)

        msg = json.loads(message)
        jsonschema.validate(msg, MESSAGE_FORMAT)

        msg_data = msg["data"]
        cmd = msg_data["command"]
        args = msg_data.get("arguments", {})
        id = msg_data["id"]

        # Call command in thread pool
        @in_thread
        def t_wrap():
            val = self.rpc_server._call_command(self, cmd, args)
            if val is None:
                val = {}
            return val

        res = yield t_wrap()

        response = {
            "type": "response",
            "data": res,
            "id": id
        }

        str_response = json.dumps(response)
        self.write_message(str_response)

    def on_close(self):
        self.on_socket_close.fire()

