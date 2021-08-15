from rebelykos.core.client.utils import register_cli_cmds

@register_cli_cmds
class Listeners:
    name = "listeners"
    description = "Listeners menu"
    _remote = True

    def __init__(self):
        self.prompt = None
        self.available = []
        self._selected = None

    @property
    def selected(self):
        return self._selected