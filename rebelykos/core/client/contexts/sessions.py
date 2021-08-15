from rebelykos.core.client.utils import register_cli_cmds


@register_cli_cmds
class Sessions:
    name = "sessions"
    description = "Sessions menu"
    _remote = True

    def __init__(self):
        self._selected = None
        self.prompt = None

    @property
    def selected(self):
        return self._selected
