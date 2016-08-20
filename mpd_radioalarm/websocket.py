from tornado.websocket import WebSocketHandler as TornWebSocketHandler
from tornado.gen import coroutine
import json
import jsonschema

from mpd_radioalarm.handler import BaseHandler as RequestBaseHandler
from mpd_radioalarm.data import in_thread
from mpd_radioalarm import config
from mpd_radioalarm.eventhook import EventHook

_commands = {}
print('commands altered')
_topics = {}

def add_command(name, func):
    _commands[name] = func

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


def update_topic(topic, update):
    msg = {
        "type": "update",
        "topic": topic,
        "data": update
    }
    str_msg = json.dumps(msg)

    for sock in _topics[topic]:
        sock.write_message(str_msg)


def add_topic(topic):
    _topics[topic] = []


def subscribe(socket, topic):
    socket.on_socket_close.addHandler(lambda : _topics[topic].remove(socket))
    _topics[topic].append(socket)
    return {
        'success': True,
        'topic': topic
    }


add_command('subscribe', subscribe)

class WebSocketHandler(TornWebSocketHandler):
    def initialize(self):
        RequestBaseHandler.initialize(self)
        self.on_socket_close = EventHook()

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

        @in_thread
        def t_wrap():
            return _commands[cmd](self, **args)

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

