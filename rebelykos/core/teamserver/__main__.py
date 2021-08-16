#! /usr/bin/env python3

"""
Usage: teamserver [-h] [--port <PORT>] [--insecure] <host> <password>

optional arguments:
    -h, --help         Show this help message and exit
    -p, --port <PORT>  Port to bind to [default: 5000]
    --insecure         Start server without TLS
"""

import asyncio
from termcolor import colored
import hmac
import http
import logging
import os
from hashlib import sha512
import signal
import websockets
from websockets import WebSocketServerProtocol

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
    get_path_in_data_folder,
    decode_auth_header
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

    async def connection_handler(self, websocket, path):
        # try:
        #     user = await self.
        while True:
            try:
                data = await asyncio.wait_for(websocket.recv(), timeout=20)
            except asyncio.TimeoutError:
                logging.debug(f"No data")
            else:
                pass
                # await self.process_client_msg(

class RLWebSocketServerProtocol(WebSocketServerProtocol):
    ts_digest = None

    async def process_request(self, path, req_headers):
        try:
            username, password_digest = decode_auth_header(req_headers)
            if not hmac.compare_digest(password_digest,
                                       RLWebSocketServerProtocol.ts_digest):
                logging.error(f"User {username} failed authentication")
                return http.HTTPStatus.UNAUTHORIZED, [], b"UNAUTHORIZED\n"
        except KeyError:
            logging.error("Received handshake with no authorization header")
            return htttp.HTTPStatus.FORBIDDEN, [], b"FORBIDDEN\n"

        logging.info(f"User {username} authenticated successfully")

async def server(stop, args, ts_digest):
    if not os.path.exists(get_path_in_data_folder("rl.db")):
        logging.info("Creating database")
        await AsyncRLDatabase.create_db_and_schema()

    # test
    # async with AsyncRLDatabase() as db:
    #     async for row in db.get_profiles():
    #         print(row)

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
    #     logging.warning()
    RLWebSocketServerProtocol.ts_digest = ts_digest
    async with websockets.serve(
        ts.connection_handler,
        host=args["<host>"],
        port=int(args["--port"]),
        create_protocol=RLWebSocketServerProtocol,
        ssl=ssl_context,
        ping_interval=None,
        ping_timeout=None
    ):

        logging.info(colored(f"Teamserver started on {args['<host>']}:"
                             f"{args['--port']}", "yellow"))
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
