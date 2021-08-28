import logging

from rebelykos.core.teamserver.db import AsyncRLDatabase, RLDatabase
from rebelykos.core.utils import CmdError


class Profiles:
    name = "profiles"
    description = "Profiles menu"

    def __init__(self, teamserver):
        self.teamserver = teamserver
        self.profiles = set()
        self.selected = None

    def get_selected(self):
        if self.selected:
            return self.selected

    def info(self):
        if not self.selected:
            raise CmdError("No profile selected")
        return self.selected

    def set(self, name: str, value: str):
        if not self.selected:
            raise CmdError("No profile selected")
        try:
            self.selected[name] = value
        except KeyError:
            raise CmdError(f"Unknown option '{name}'")

    def use(self, name: str):
        with RLDatabase() as db:
            for p in db.get_profiles():
                if name == p[1]:
                    self.selected = {**{x: p[i] for i, x
                                     in enumerate(("profile",
                                                   "access_key_id",
                                                   "secret_access_key",
                                                   "session_token",
                                                   "region"),
                                                  1)},
                                     "name": name}
                    return self.selected
        logging.debug(f"profile {name} does not exist")
        self.selected = {"profile": name,
                         "access_key_id": "",
                         "secret_access_key": "",
                         "session_token": "",
                         "region": "",
                         "name": name}
        return self.selected

    def __iter__(self):
        yield ("profiles", len(self.profiles))

    def __str__(self):
        return self.__class__.__name__.lower()
