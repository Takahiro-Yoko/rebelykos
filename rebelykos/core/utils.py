import logging
import os
import random
import string

class CmdError(Exception):
    def __init__(self, msg):
        logging.error(msg)
        super().__init__(msg)

def gen_random_string(length: int = 10):
    return "".join([random.choice(string.ascii_letters + string.digits)
                    for _ in range(length)])

def get_data_folder():
    return os.path.expanduser("~/.rl")

def get_path_in_data_folder(path):
    return os.path.join(get_data_folder(), path.lstrip("/"))
