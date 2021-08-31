import asyncio
import logging
from typing import List

from terminaltables import SingleTable

from rebelykos.core.utils import (
    gen_random_string,
    print_bad,
    print_info,
)
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
                elif k.startswith("<"):
                    normalized_args[k[1:-1]] = v
                elif k.startswith("--"):
                    normalized_args[k[2:]] = v

            msg = {"id": gen_random_string(),
                   "ctx": ctx,
                   "cmd": cmd,
                   "args": normalized_args,
                   "data": data
            }

            return await self.selected.send(msg)

        print_bad("Not connected to a teamserver")

    @cmd
    def connect(self, URL: List[str]):
        """
        Connect to the specified teamserver(s)

        Usage: connect [-h] <URL>...

        Arguments:
            URL teamserver url(s)
        """
        for url in URL:
            conn = ClientConnection(url)
            conn.start()
            self.connections.append(conn)
            self.selected = self.selected or conn

    @cmd
    def disconnect(self, TS: List[str]):
        """
        Disconnect from the specified teamserver(s)

        Usage: disconnect [-h] <TS>...

        Arguments:
            TS teamserver(s) to disconnect from
        """
        for ts in self.connections:
            for to_disconnect in TS:
                if ts.alias == to_disconnect:
                    ts.stop()
                    if self.selected and self.selected.alias == ts.alias:
                        self.selected = None
                    del self.connections[self.connections.index(ts)]

    @cmd
    def use(self, TS: str):
        """
        Select a specified teamserver for all communication

        Usage: use [-h] <TS>

        Arguments:
            TS teamserver to use
        """
        for ts in self.connections:
            if not ts.stats.CONNECTED:
                logging.error(f"Teamserver {ts} cannot use"
                              " (maybe invalid connection)")
                del self.connections[self.connections.index(ts)]
            elif ts.alias == TS:
                self.selected = ts
                print_info(f"Now using {TS} for all comms")
                return

        print_bad(f"Not currently connected to teamserver '{TS}'")

    @cmd
    def rename(self, old_name: str, new_name: str):
        """
        Rename a specified teamserver

        Usage: use [-h] <old_name> <new_name>

        Arguments:
            old_name    old teamserver name
            new_name    new teamserver name
        """
        for ts in self.connections:
            if not ts.stats.CONNECTED:
                logging.error(f"Teamserver {ts} cannot rename"
                              " (maybe invalid connection)")
                del self.connections[self.connections.index(ts)]
            elif ts.alias == old_name:
                ts.alias = new_name
                print_info(f"Renamed teamserver {old_name} to {new_name}")
                return
        print_bad(f"No teamserver {old_name} found")

    @cmd
    def list(self):
        """
        Show available teamservers

        Usage: list [-h]
        """
        self.connections = [conn for conn in self.connections
                            if conn.stats.CONNECTED]
        if self.connections:
            table_data = [["Alias", "URL"]]
            table_data.extend([f"*{ts.alias}" if self.selected == ts
                               else ts.alias, str(ts)]
                              for ts in self.connections)
            table = SingleTable(table_data, title="Teamservers")
            table.inner_row_border = True
            print(table.table)
