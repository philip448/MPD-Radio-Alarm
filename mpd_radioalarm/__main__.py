from mpd_radioalarm.server import Server
from mpd_radioalarm.plugins import import_plugins


def run_mpd_radioalarm():
    app = Server()
    import_plugins(app)
    app.start()

if __name__ == '__main__':
    run_mpd_radioalarm()