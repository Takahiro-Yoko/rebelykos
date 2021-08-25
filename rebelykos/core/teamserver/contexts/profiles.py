import logging

from rebelykos.core.teamserver.db import AsyncRLDatabase, RLDatabase
from rebelykos.core.teamserver.loader import Loader
from rebelykos.core.utils import get_path_in_package


class Profiles(Loader):
    name = "profiles"
    description = "Profiles menu"

    def __init__(self, teamserver):
        self.teamserver = teamserver
        self.profiles = []
        self.selected = None
        super().__init__(
            type="profile",
            paths=[get_path_in_package("core/teamserver/profiles")]
        )

    def get_selected(self):
        if self.selected:
            return dict(self.selected)

    def use(self, name: str):
        with RLDatabase() as db:
            for p in db.get_profiles():
                if name == p[1]:
                    self.selected = p
                    return {**{x: p[i] for i, x
                               in enumerate(("profile",
                                             "access_key_id",
                                             "secret_access_key",
                                             "session_token",
                                             "region"),
                                            1)},
                            "name": name}
        logging.debug(f"profile {name} does not exist")
        return {"profile": name,
                "access_key_id": "",
                "secret_access_key": "",
                "session_token": "",
                "region": "",
                "name": name}
            

    def __iter__(self):
        yield ("loaded", len(self.loaded))

    def __str__(self):
        return self.__class__.__name__.lower()
