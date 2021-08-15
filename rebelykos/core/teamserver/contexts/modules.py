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
