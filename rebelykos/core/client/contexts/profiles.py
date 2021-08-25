from rebelykos.core.client.utils import cmd, register_cli_cmds


@register_cli_cmds
class Profiles:
    name = "profiles"
    description = "Profiles menu"
    _remote = True

    def __init__(self):
        self.prompt = None
        self.available = []
        self._selected = None

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, data):
        self.prompt = f"(<ansired>{data['name']}</ansired>)"
        self._selected = data

    @cmd
    def use(self, name: str, response):
        """
        Select the specified profile

        Usage: use <name> [-h]

        Arguments:
            name  profile to select
        """
        self.selected = response.result
