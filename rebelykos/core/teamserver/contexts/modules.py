import asyncio
from rebelykos.core.events import Events
from rebelykos.core.teamserver.db import RLDatabase
from rebelykos.core.teamserver.loader import Loader
from rebelykos.core.utils import CmdError, get_path_in_package
from rebelykos.core.teamserver.job import Job


class Modules(Loader):
    name = "modules"
    description = "Modules menu"

    def __init__(self, teamserver):
        self.teamserver = teamserver
        self.modules = []
        self.selected = None
        super().__init__(
            type="module",
            paths=[get_path_in_package("core/teamserver/modules")]
        )

    def list(self, name: str = None):
        return {m.name: m.description for m in self.loaded}

    def use(self, name: str):
        for m in self.loaded:
            if m.name.lower() == name.lower():
                self.selected = m
                return dict(self.selected)
        raise CmdError(f"No module available named '{name.lower()}'")

    def options(self):
        if not self.selected:
            raise CmdError("No modules selected")
        return self.selected.options

    def info(self):
        if not self.selected:
            raise CmdError("No module selected")
        return dict(self.selected)

    def set(self, name: str, value: str):
        if not self.selected:
            raise CmdError("No module selected")
        try:
            if name.lower() == "profile":
                with RLDatabase() as db:
                    for row in db.get_profiles():
                        if value.lower() == row[1].lower():
                            value = {"aws_access_key_id": row[2],
                                     "aws_secret_access_key": row[3],
                                     "region_name": row[4],
                                     "aws_session_token": row[5]}
                            break
                if not isinstance(value, dict):
                    raise CmdError(f"Invalid profile: {value}")
            self.selected[name] = value
        except KeyError:
            raise CmdError(f"Unknown option '{name}'")

    def run(self):
        if not self.selected:
            raise CmdError("No module selected")
        elif not all(v["Value"] for v in self.selected.options.values()
                     if v["Required"]):
            raise CmdError("Required option(s) not set")
        return self.selected.run()

    def reload(self):
        self.get_loadables()
        if self.selected:
            self.use(self.selected.name)

        asyncio.create_task(self.teamservers.update_available_loadables())

    def get_selected(self):
        if self.selected:
            return dict(self.selected)

    def __iter__(self):
        yield ("loaded", len(self.loaded))

    def __str__(self):
        return self.__class__.__name__.lower()
