#! /usr/bin/env python3

"""
Usage: client [-h] [-d] [<URL>...]

arguments:
    URL teamserver url(s)

options:
    -h, --help    Show this help message and exit
    -d, --debug   Enable debug output
"""

import logging
import asyncio

from rebelykos.core.client.cmdloop import RLShell

async def main(args):
    s = RLShell(args)
    try:
        await s.cmdloop()
    except (KeyboardInterrupt, SystemExit):
        print("Exiting")

def start(args):
    log_level = logging.DEBUG if args['--debug'] else logging.INFO
    logging.basicConfig(format=("%(asctime)s [%(levelname)s]"
                                " - %(filename)s: %(funcName)s"
                                " - %(message)s"),
                        level=log_level)
    logging.getLogger('websockets').setLevel(log_level)
    asyncio.run(main(args))
