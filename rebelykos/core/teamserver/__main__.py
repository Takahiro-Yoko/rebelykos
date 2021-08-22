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
import json
import logging
import os
from hashlib import sha512
import signal
import ssl
import websockets
from websockets import WebSocketServerProtocol

from rebelykos.core.events import Events
from rebelykos.core.utils import create_self_signed_cert
from rebelykos.core.teamserver.db import AsyncRLDatabase
from rebelykos.core.teamserver.users import Users, UsernameAlreadyPresentError
from rebelykos.core.teamserver.contexts import (
    # Listeners,
    # Sessions,
    Modules,
    # Stagers
)
from rebelykos.core.utils import (
    get_data_folder,
    get_path_in_data_folder,
    decode_auth_header,
    CmdError,
    get_ips
)

class TeamServer:
    def __init__(self):
        self.users = Users()
        # self.loop = asyncio.get_running_loop()
        self.contexts = {
            # 'listeners': Listeners(self),
            # 'sessions': Sessions(self),
            'modules': Modules(self),
            # 'stagers': Stagers(self),
            # 'users': self.users
        }

    async def process_client_msg(self, user, path, data):
        msg = json.loads(data)
        logging.debug(f"Received message from {user.name}@{user.ip} "
                      f"path:{path} msg: {msg}")
        status = "error"

        try:
            ctx = self.contexts[msg["ctx"].lower()]
        except KeyError:
            traceback.print_exc()
            result = f"Context '{msg['ctx'].lower()}' does not exist"
            logging.error(result)
        else:
            try:
                cmd_handler = getattr(ctx, msg["cmd"])
                result = cmd_handler(**msg["args"])
                status = "success"
            except AttributeError:
                traceback.print_exc()
                result = (f"Command '{msg['cmd']}' does not exist in context "
                          f" '{msg['ctx'].lower()}'")
            except CmdError as e:
                result = str(e)
            except Exception as e:
                traceback.print_exc()
                result = (f"Exception when executing command '{msg['cmd']}': "
                          f"{e}")
                logging.error(result)

        await user.send({
            "type": "message",
            "id": msg["id"],
            "ctx": msg["ctx"],
            "name": msg["cmd"],
            "status": status,
            "result": result
        })

    async def update_server_stats(self):
        stats = {**{str(ctx): dict(ctx) for ctx in self.contexts.values()},
                 "ips": get_ips()}
        await self.users.broadcast_event(Events.STATS_UPDATE, stats)

    async def update_available_loadables(self):
        loadables = {str(ctx): [loadable.name for loadable in ctx.loaded]
                     for ctx in self.contexts.values()
                     if hasattr(ctx, "loaded")}
        await self.users.broadcast_event(Events.LOADABLES_UPDATE, loadables)

    async def connection_handler(self, websocket, path):
        try:
            user = await self.users.register(websocket)
            await self.update_server_stats()
            await self.update_available_loadables()
            logging.info(f"New client connected {user.name}@{user.ip}")
        except UsernameAlreadyPresentError as e:
            logging.error(f"{websocket.remote_address[0]}: {e}")
            return

        while True:
            try:
                data = await asyncio.wait_for(websocket.recv(), timeout=20)
            except asyncio.TimeoutError:
                logging.debug(f"No data from {user.name}@{user.ip}"
                              " after 20 seconds, sending ping")
                try:
                    pong_waiter = await websocket.ping()
                    await asyncio.wait_for(pong_waiter, timeout=10)
                except asyncio.TimeoutError:
                    logging.debug(f"No pong from {user.name}@{user.ip} "
                                  "after 10 seconds, closing connection")
                    self.users.unregister(user.name)
                    await self.update_server_stats()
                    return 
            except websockets.exceptions.ConnectionClosed:
                logging.debug(f"Connection closed by client")
                self.users.unregister(user.name)
                await self.update_server_stats()
                return
            else:
                await self.process_client_msg(user, path, data)

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
    if not args["--insecure"]:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        try:
            ssl_context.load_cert_chain(get_path_in_data_folder("chain.pem"))
        except FileNotFoundError:
            create_self_signed_cert()
            ssl_context.load_cert_chain(get_path_in_data_folder("chain.pem"))

        # server_cert_fingerprint = get_cert_fingerprint(
        #     get_path_in_data_folder("cert.pem")
        # )
        # logging.warning()

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
    stop = asyncio.Future()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set_result, None)

    if args["--insecure"]:
        logging.warning("SECURITY WARNING: --insecure flag passed, "
                        "communication between client and server "
                        "will be in cleartext!")

    ts_digest = hmac.new(args["<password>"].encode(), msg=b"rebelykos",
                         digestmod=sha512).hexdigest()
    loop.run_until_complete(server(stop, args, ts_digest))
