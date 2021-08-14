import logging
import random
import string

class CmdError(Exception):
    def __init__(self, msg):
        logging.error(msg)
        super().__init__(msg)

def gen_random_string(length: int = 10):
    return "".join([random.choice(string.ascii_letters + string.digits)
                    for _ in range(length)])
