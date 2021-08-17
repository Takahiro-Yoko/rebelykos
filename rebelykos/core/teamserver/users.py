class User:
    def __init__(self, name, websocket):
        self.name = name
        self.websocket = websocket
        self.ip, self.port = websocket.remote_address

class Users:
    def __init__(self):
        self.users = set()

class UsernameAlreadyPresentError(Exception):
    pass
