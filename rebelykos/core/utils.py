import logging
import os
import random
import string

import rebelykos

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

def get_path_in_package(path):
    return os.path.join(os.path.dirname(rebelykos.__file__), path.lstrip("/"))

def decode_auth_header(req_headers):
    auth_header = req_headers["Authorization"]
    auth_header = b64decode(auth_header)
    username, password_digest = auth_header.decode().split(":")
    return username, password_digest

def get_ips():
    ips = []
    for iface in netifaces.interfaces():
        try:
            netif = netifaces.ifaddresses(iface)
            if netif[netifaces.AF_INET][0]["addr"] == "127.0.0.1":
                continue
            ips.append(netif[netifaces.AF_INET][0]["addr"])
        except (ValueError, KeyError):
            continue

    return ips
