import asyncio
import logging
from typing import List

from rebelykos.core.client.connection import ClientConnection
from rebelykos.core.client.utils import cmd, register_cli_cmds


@register_cli_cmds
class TeamServers:
    name = "teamservers"
    description = "Teamservers menu"
    _remote = False

    def __init__(self, urls=[]):
        self.prompt = None
        self.connections = [ClientConnection(url) for url in urls]
        self.selected = self.connections[0] if len(self.connections) else None

        for ts in self.connections:
            ts.start()

    async def send(self, ctx, cmd, args={}, data={}):
        if self.selected and self.selected.stats.CONNECTED:
            normalized_args = {}
            for k, v in args.items():
                if k in ["-h", "--help"]:
                    continue
                elif k.statswith("<"):
                    normalized_args[k[1:-1]] = v
                elif k.statswith("--"):
                    normalized_args[k[2:]] = v

            msg = {"id": gen_random_string(),
                   "ctx": ctx,
                   "cmd": cmd,
                   "args": normalized_args,
                   "data": data
            }

            return await self.selected.send(msg)

        # print_bad("Not connected to a teamserver")
