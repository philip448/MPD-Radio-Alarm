RPCClient = function () {
    var ws;
    var connection_established = false;
    var self = this;

    var open_calls = {};
    var subscriptions = {};


    var message_types = {
        response: function (data) {
            var id = data.id;
            if (open_calls[id]) {
                open_calls[id](data.data);
                delete open_calls[id];
            }
        },

        update: function (data) {
            var topic = data.topic;
            if (subscriptions[topic]) {
                subscriptions[topic].forEach(function (fn) {
                    fn(data.data);
                });
            }
        }
    };

    function generate_id() {
        return Math.random().toString(36).substring(7);
    }

    function on_message(message) {
        data = JSON.parse(message);

        var func = message_types[data.type];
        if (!func) {
            throw "Invalid message type: " + data.type;
        }

        func(data);
    }

    this.connect = function (url, callback) {
        ws = new WebSocket(url);
        ws.onopen = function () {
            window.onbeforeunload = function () {
                ws.close();
            };
            connection_established = true;
            if (callback) {
                callback();
            }
        };

        ws.onmessage = function (evt) {
            on_message(evt.data);
        };
    };

    this.call = function (command, arguments, callback) {
        if (!connection_established) {
            throw "Connection not ready";
        }

        var id = generate_id();

        open_calls[id] = function(data) {
            if (callback) {
                callback(data);
            }
        };

        msg = {
            type: "call",
            data: {
                command: command,
                arguments: arguments,
                id: id
            }
        };

        ws.send(JSON.stringify(msg));
    };

    this.subscribe = function (topic, func, on_success) {
        this.call('subscribe', { topic: topic }, function (evt) {
            if (!subscriptions[topic]) {
                subscriptions[topic] = [];
            }

            subscriptions[topic].push(func);

            if (on_success) {
                on_success();
            }
        });
    }


};