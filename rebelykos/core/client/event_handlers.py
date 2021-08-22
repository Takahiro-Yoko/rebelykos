import logging


class ClientEventHandlers:
    def __init__(self, connection):
        self.connection = connection

    def stats_update(self, data):
        logging.debug(f"in stats_update event handler, got: {data}")
        # self.connection.stats.LISTENERS = data["listeners"]
        # self.connection.stats.SESSIONS = data["sessions"]
        self.connection.stats.USERS = data["users"]
        # self.connection.stats.IPS = data["ips"]

    def loadables_update(self, data):
        for ctx, loadables in data.items():
            for lctx in self.connection.contexts:
                if lctx.name == ctx:
                    lctx.available = loadables
