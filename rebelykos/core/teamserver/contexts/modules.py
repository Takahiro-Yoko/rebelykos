from rebelykos.core.teamserver import ipc_server
from rebelykos.core.teamserver.loader import Loader
from rebelykos.core.utils import get_path_in_package


class Modules(Loader):
    name = "modules"
    description = "Modules menu"

    def __init__(self, teamserver):
        self.teamserver = teamserver
        self.modules = []
        self.selected = None
        super().__init__(
            type="module",
            paths=[get_path_in_package("core/teamserver/modules/python")]
        )

    def get_selected(self):
        if self.selected:
            return dict(self.selected)

    def __iter__(self):
        yield ("loaded", len(self.loaded))

    def __str__(self):
        return self.__class__.__name__.lower()
