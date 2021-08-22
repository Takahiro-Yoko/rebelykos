import logging


class ServerResponse:
    def __init__(self, res, conn):
        self.raw = res
        self.conn = conn

        for k, v in res.items():
            setattr(self, k, v)
