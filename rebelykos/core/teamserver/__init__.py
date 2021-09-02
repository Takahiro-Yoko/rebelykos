import logging


logging.basicConfig(
    format=("%(asctime)s %(process)d %(threadName)s - [%(levelname)s] "
            "%(filename)s: %(funcName)s - %(message)s"),
    level=logging.DEBUG
)

logging.getLogger("websockets.server").setLevel(logging.ERROR)
logging.getLogger("websockets.protocol").setLevel(logging.ERROR)
