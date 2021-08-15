#! /usr/bin/env python3

"""
Usage: teamserver [-h] [--port <PORT>] [--insecure] <host> <password>

optional arguments:
    -h, --help         Show this help message and exit
    -p, --port <PORT>  Port to bind to [default: 5000]
    --insecure         Start server without TLS
"""

import asyncio
import hmac
import logging
import os
from hashlib import sha512
import signal

from rebelykos.core.teamserver.db import AsyncRLDatabase
# from rebelykos.core.teamserver.users import Users
from rebelykos.core.teamserver.contexts import (
    # Listeners,
    # Sessions,
    Modules,
    # Stagers
)
from rebelykos.core.utils import (
    get_data_folder,
    get_path_in_data_folder
)

class TeamServer:
    def __init__(self):
        # self.users = Users()
        self.loop = asyncio.get_running_loop()
        self.contexts = {
            # 'listeners': Listeners(self),
            # 'sessions': Sessions(self),
            'modules': Modules(self),
            # 'stagers': Stagers(self),
            # 'users': self.users
        }

async def server(stop, args, ts_digest):
    if not os.path.exists(get_path_in_data_folder("rl.db")):
        logging.info("Creating database")
        await AsyncRLDatabase.create_db_and_schema()

    # test
    # db = AsyncRLDatabase()
    # async with db:
    #     # await db.add_profile("profile", "key", "secret", "ap-northeast")
    #     for pro in db.get_profiles():
    #         print(pro)
        # for pro in pros:
        #     print(pro)
    # for profile in db.get_profiles():
    #     print(profile)

    ts = TeamServer()

    ssl_context = None
    # if not args["--insecure"]:
    #     ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    #     try:
    #         ssl_context.load_cert_chain(get_path_in_data_folder("chain.pem"))
    #     except FileNotFoundError:
    #         create_self_signed_cert()
    #         ssl_context.load_cert_chain(get_path_in_data_folder("chain.pem"))

    #     sever_cert_fingerprint = get_cert_fingerprint(
    #         get_path_in_data_folder("cert.pem")
    #     )
    #     # logging.warning(
    # async with websockets.serve(
    #     ts.connection_handler,
    #     host=args["<host>"],
    #     port=int(args["--port"]),
    #     create_protocol=RLWebSocketServerProtocol,
    #     ssl=ssl_context,
    #     ping_interval=None,
    #     ping_timeout=None
    # ):

    await stop

def start(args):
    if not os.path.exists(get_data_folder()):
        logging.info("First time use detected, creating data folder (~/.rl)")
        os.makedirs(get_path_in_data_folder("logs"))
    if not os.path.exists(get_path_in_data_folder("logs")):
        os.mkdir(get_path_in_data_folder("logs"))
    
    loop = asyncio.get_event_loop()
    ts_digest = hmac.new(args["<password>"].encode(), msg=b"rebelykos",
                         digestmod=sha512).hexdigest()
    stop = asyncio.Future()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set_result, None)

    if args["--insecure"]:
        logging.warning("SECURITY WARNING: --insecure flag passed, "
                        "communication between client and server "
                        "will be in cleartext!")

    loop.run_until_complete(server(stop, args, ts_digest))
