from terminaltables import SingleTable

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
    def set(self, name: str, value: str, response):
        """
        Set aws settings on the selected profile

        Usage: set <name> <value> [-h]

        Arguments:
            name name
            value value
        """

    @cmd
    def info(self, response):
        """
        Show detailed information of the selected profile

        Usage: info [-h]
        """
        table_data = [["profile", "access_key_id", "secret_access_key",
                       "region", "session_token"]]
        table_data.append([response.result[k] for k in table_data[0]])
        table = SingleTable(table_data, title=self.selected["name"])
        print(table.table)

    @cmd
    def use(self, name: str, response):
        """
        Select the specified profile

        Usage: use <name> [-h]

        Arguments:
            name  profile to select
        """
        self.selected = response.result
