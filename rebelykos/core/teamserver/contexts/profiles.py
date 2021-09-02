from rebelykos.core.teamserver.db import RLDatabase
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
        elif name in self.selected:
            self.selected[name] = value
        else:
            raise CmdError(f"Unknown option '{name}'")

    def use(self, name: str):
        with RLDatabase() as db:
            for p in db.get_profiles():
                if name == p[1]:
                    self.selected = {**{x: p[i] for i, x
                                     in enumerate(("profile",
                                                   "access_key_id",
                                                   "secret_access_key",
                                                   "region",
                                                   "session_token"),
                                                  1)},
                                     "name": name}
                    return self.selected
        self.selected = {"profile": name,
                         "access_key_id": "",
                         "secret_access_key": "",
                         "region": "",
                         "session_token": "",
                         "name": name}
        return self.selected

    def update(self):
        if not self.selected:
            raise CmdError("No profile selected")
        elif all(self.selected[k] for k in ("profile", "access_key_id",
                                            "secret_access_key", "region")):
            with RLDatabase() as db:
                db.upsert(self.selected)
        else:
            raise CmdError("Required option(s) not set")

    def list(self):
        with RLDatabase() as db:
            return [row[1:] for row in db.get_profiles()]
        return []

    def remove(self, profile):
        with RLDatabase() as db:
            return db.remove(profile)

    def __iter__(self):
        yield ("profiles", len(self.profiles))

    def __str__(self):
        return self.__class__.__name__.lower()
