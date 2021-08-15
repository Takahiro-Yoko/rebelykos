import logging
import functools
import random
import traceback
from time import sleep
from threading import Thread
from secrets import token_bytes
from collections import defaultdict
from multiprocessing.connection import Listener, Client

from rebelykos.core.events import Events


class IPCServer(Thread):

    def __init__(self, address=("127.0.0.1", random.randint(60000, 65530)),
                 authkey=token_bytes(15)):
        super().__init__()
        self.name = "IPCServer"
        self.address = address
        self.authkey = authkey
        self.daemon = True
        self.subscribers = defaultdict(set)

    def run(self):
        with Listener(self.address, authkey=self.authkey) as listener:
            logging.debug(f"Started IPC server on {self.address[0]}:"
                          f"{self.address[1]}")
            while True:
                client = listener.accept()
                t = Thread(target=self.wait_for_event, args=(client, listener))
                t.setDaemon(True)
                t.start()

    def attach(self, event, func):
        logging.debug(f"Attaching event: {event.name} -> {func.__qualname__}")
        self.subscribers[event].add(func)

    def detach(self, event, func):
        raise NotImplementedError

    def publish_event(selff, topic, msg):
        for sub in self.subscribers.get(topic, []):
            return sub(*msg)

    def wait_for_event(self, client, listener):
        logging.debug(f"Connection accepted from {listener.last_accepted[0]}"
                      f":{listener.last_accepted[1]}")
        while True:
            try:
                data = client.recv()
            except EOFError:
                continue
            else:
                topic, data = data
                logging.debug(
                    f"Got event: {topic} "
                    f"{f'- msg-len: {len(msg)}' if msg else ''}"
                )
                if topic in self.subscribers:
                    for sub in self.subscribers[topic]:
                        try:
                            client.send((topic, sub(msg)))
                        except Exception as e:
                            logging.error("Error occured in subscriber "
                                          f"function to {topic} event, "
                                          "printing traceback")
                            traceback.print_exc()
                            client.send((Events.EXCEPTION, str(e)))
                else:
                    logging.warning(f"Got event: {topic}, but there's "
                                    "nothing subscribed")
