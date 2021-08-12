import logging

class CmdError(Exception):
    def __init__(self, msg):
        logging.error(msg)
        super().__init__(msg)
