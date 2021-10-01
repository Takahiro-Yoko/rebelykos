import json
from terminaltables import SingleTable

from rebelykos.core.response import Response as res
from rebelykos.core.utils import (
    print_bad,
    print_good,
    print_info,
)
from rebelykos.core.client.utils import (
    cmd,
    register_cli_cmds
)


@register_cli_cmds
class Modules:
    name = "modules"
    description = "Modules menu"
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
        Select the specified module

        Usage: use <name> [-h]

        Arguments:
            name  module to select
        """
        self.selected = response.result

    @cmd
    def list(self, name: str, response):
        """
        Get available modules

        Usage: list [-h] [<name>]

        Arguments:
            name  filter by module name
        """
        table_data = [["Name", "Description"]]
        table_data.extend([m_name, m_desc] for m_name, m_desc
                          in response.result.items())
        table = SingleTable(table_data, title="Modules")
        table.inner_row_border = True
        print(table.table)

    @cmd
    def options(self, response):
        """
        Show selected module options

        Usage: options [-h]
        """
        table_data = [["Option Name", "Required", "Value", "Description"]]
        table_data.extend([k, v["Required"], v["Value"], v["Description"]]
                          for k, v in response.result.items())
        table = SingleTable(table_data, title=self.selected["name"])
        table.inner_row_border = True
        print(table.table)

    @cmd
    def info(self, response):
        """
        Show detailed information of the selected module

        Usage: options [-h]
        """
        print(f"Author(s): {response.result['author']}")
        print(f"Description: {response.result['description']}")
        print(f"Language: {response.result['language']}\n")

        table_data = [["Option Name", "Required", "Value", "Description"]]
        table_data.extend([k, v["Required"], v["Value"], v["Description"]]
                          for k, v in response.result["options"].items())
        table = SingleTable(table_data, title=self.selected["name"])
        table.inner_row_border = True
        print(table.table)

    @cmd
    def run(self, response):
        """
        Run a module

        Usage:
            run [-h]
        """
        k, v = response.result
        if k == res.GOOD:
            print_good(v)
        elif k == res.INFO:
            print_info(v)
        elif k == res.BAD:
            print_bad(v)
        elif k == res.RESULT:
            print(json.dumps(v, indent=2, sort_keys=True))

    @cmd
    def reload(self, response):
        """
        Reload all modules

        Usage: reload [-h]
        """

    @cmd
    def set(self, name: str, value: str, response):
        """
        Set options on the selected module

        Usage: set <name> <value> [-h]

        Arguments:
            name   option name
            value  option value
        """

    @cmd
    def unset(self, name: str, response):
        """
        Unset options on the selected module

        Usage: unset <name> [-h]

        Arguments:
            name    option name
        """
