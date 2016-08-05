MPClient = function() {
    var debug = {{ debug }};
    var ws;
    var subscriptions = {}
    var wait_response = {};

    var connection_established = false;

    var generate_id = function() {
        return Math.random().toString(36).substring(7);
    };

    this.connect = function (callback) {
        ws = new WebSocket("{{ ws_url }}");
        ws.onopen = function() {
            callback();

            window.onbeforeunload = function() {
                ws.close();
            };
        };

        ws.onmessage = function (evt) {
            data = JSON.parse(evt.data);



            switch(data.type) {
                case "update":
                    var topic = data.topic;
                    if (subscriptions[topic]) {
                        subscriptions[topic].forEach(function(fn){
                            fn(data.data);
                        });
                    }
                    break;

                case "response":
                    var id = data.id;
                    if(wait_response[id]) {
                        wait_response[id](data.data);
                        delete wait_response;
                    }
                    break;
            }
        };
    }; // end connect


        // Public functions


    this.call = function(command, arguments, callback) {
        if (!connection_established) {
            throw new Exception()
            return;
        }

        var id = generate_id();

        wait_response[id] = callback;

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

    this.subscribe = function(topic, func) {
        this.call('subscribe', {topic: topic}, function(evt) {
             if (!subscriptions[topic]) {
                subscriptions[topic] = [];
             }

             subscriptions[topic].push(func);
        });
    };
};