import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "check_root"
        self.description = ("Check if the account has root"
                            " or elevated IAM privileges")
        self.author = "Takahiro Yokoyama"

    def run(self):
        result = []
        client = boto3.client("iam", **self["profile"])
        result.extend(self._handle_err(client.get_account_summary))
        result.extend(self._handle_err(client.list_users, key="Users"))

        if result[-1][0] == res.RESULT:
            users = result[-1][1]
            result.append((res.INFO, "Checking for console access"))
            for user in users:
                user = user["UserName"]
                result.extend(self._handle_err(client.get_login_profile,
                                               UserName=user))
                if result[-1][0] == res.RESULT:
                    result.extend(
                        self._handle_err(
                            client.list_mfa_devices,
                            key="MFADevices",
                            msg=(f"User {user} likely has console access"
                                 " and the password can be reset :-)"),
                            UserName=user
                        )
                    )
        return result
