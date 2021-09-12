import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "list_roles"
        self.description = "Just list all role-names"
        self.author = "Takahiro Yokoyama"
        self.options["show-arn"] = {
            "Description": ("Show role-arn with role-name"
                            " if true or True specified"),
            "Required": False,
            "Value": False
        }

    def run(self):
        result = []
        client = boto3.client("iam", **self["profile"])
        result.extend(self._handle_err(client.list_roles, key="Roles"))
        if result[-1][0] == res.RESULT:
            roles = result.pop()[1]
            if self["show-arn"] and self["show-arn"].lower() == "true":
                roles = [(role["RoleName"], role["Arn"]) for role in roles]
            else:
                roles = [role["RoleName"] for role in roles]
            result.append((res.RESULT, roles))
        return result
