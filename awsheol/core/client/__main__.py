#! /usr/bin/env python3

"""
Usage: client [-h]

options:
    -h, --help    Show this help message and exit
"""

import logging
import asyncio
from awsheol.core.client.cmdloop import AWShell

async def main(args):
    s = AWShell(args)
    await s.cmdloop()

def start(args):
    asyncio.run(main(args))
