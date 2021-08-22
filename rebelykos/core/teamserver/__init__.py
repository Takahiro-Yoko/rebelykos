import logging
import multiprocessing

from rebelykos.core.ipcserver import IPCServer


logging.basicConfig(
    format=("%(asctime)s %(process)d %(threadName)s - [%(levelname)s] "
            "%(filename)s: %(funcName)s - %(message)s"),
    level=logging.DEBUG
)

multiprocessing.set_start_method("fork")

ipc_server = IPCServer()
ipc_server.start()
