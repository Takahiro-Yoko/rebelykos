import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "get_password_policy"
        self.description = "Get the password policy"
        self.author = "Takahiro Yokoyama"

    def run(self):
        result = []
        client = boto3.client("iam", **self["profile"])
        result.extend(self._handle_err(client.get_account_password_policy,
                                       key="PasswordPolicy",
                                       msg="Account Password Policy"))
        return result
