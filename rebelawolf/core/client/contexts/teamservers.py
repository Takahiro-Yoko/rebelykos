import asyncio
import logging
from typing import List

from rebelawolf.core.client.connection import ClientConnection
from rebelawolf.core.client.utils import command, register_cli_cmds


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
