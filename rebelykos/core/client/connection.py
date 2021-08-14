import asyncio
import logging
import ssl
from urllib.parse import urlparse

from rebelykos.core.utils import gen_random_string
from rebelykos.core.client.stats import ClientConnectionStats
from rebelykos.core.client.event_handlers import ClientEventHandlers
from rebelykos.core.client.contexts.listeners import Listeners
from rebelykos.core.client.contexts.sessions import Sessions
from rebelykos.core.client.contexts.modules import Modules
from rebelykos.core.client.contexts.stagers import Stagers


class ClientConnection:
    def __init__(self, url: str):
        self.alias = f"TS-{gen_random_string(5)}"
        self.url = urlparse(url)
        self.stats = ClientConnectionStats()
        self.event_handlers = ClientEventHandlers(self)
        self.msg_queue = asyncio.Queue(maxsize=1)
        self.contexts = [Listeners(),
                         Sessions(),
                         Modules(),
                         Stagers()]
        self.task = None
        self.ws = None
        self.ssl_context = None

        if self.url.scheme == "wss":
            self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
        else:
            logging.warning("SECURITY WARNING: comms between client and "
                            "server will be in cleartext!")
