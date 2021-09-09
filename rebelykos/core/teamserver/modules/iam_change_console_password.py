import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "change_console_password"
        self.description = "Change the IAM console password"
        self.author = "Takahiro Yokoyama"
        self.options["user"] = {
            "Description": "User name",
            "Required": True,
            "Value": ""
        }
        self.options["password"] = {
            "Description": "New console password",
            "Required": True,
            "Value": ""
        }

    def run(self):
        result = []
        client = boto3.client("iam", **self["profile"])
        resp = self._handle_err(client.update_login_profile,
                                UserName=self["user"],
                                Password=self["password"],
                                PasswordResetRequired=False)
        if resp[-1][0] == res.RESULT:
            result.append((res.info, (f"Changing password for user: "
                                      f"{self['user']} to password: "
                                      f"{self['password']}")))
            result.append(
                (res.RESULT,
                 ("Response to password change was: "
                  f"{resp[-1][1]['ResponseMetadata']['HTTPStatusCode']}"))
            )
        else:
            result.extend(resp)

        return result
