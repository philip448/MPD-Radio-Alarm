from mpd_radioalarm.websocket import add_command, add_topic

def play(id):
    print("playing id: " + str(id))

def initialize():
    add_command('play', play)
