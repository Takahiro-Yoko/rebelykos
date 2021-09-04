import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "check_root"
        self.language = "Python"
        self.description = ("Check if the account has root"
                            " or elevated IAM privileges")
        self.author = "Takahiro Yokoyama"

    def run(self):
        client = boto3.client("iam", **self["profile"])
        result = []
        res_code, obj = self._handle_err(client.get_account_summary)
        if res_code == res.RESULT:
            result.append((res.GOOD, "Root key! or IAM access"))
            result.append((res.INFO, "Account Summary"))
            result.append((res.RESULT, obj["SummaryMap"]))
        else:
            result.append((res_code, obj))
        res_code, users = self._handle_err(client.list_users)
        if res_code == res.RESULT:
            result.append((res.INFO, "Listing Users"))
            result.append((res.RESULT, users["Users"]))
        else:
            result.append((res_code, users))

        result.append((res.INFO, "Checking for console access"))
        for user in users["Users"]:
            user = user["UserName"]
            res_code, profile = self._handle_err(
                client.get_login_profile,
                UserName=user
            )
            if res_code == res.RESULT:
                result.append((
                    res.GOOD, 
                    (f"User {user} likely has console access"
                     " and the password can be reset :-)")
                ))
                result.append((res.INFO,
                               "Checking for MFA on account"))
                res_code, mfa = self._handle_err(
                    client.list_mfa_devices,
                    UserName=user
                )
                if res_code == res.RESULT:
                    result.append((res.INFO, mfa["MFADevices"]))
                else:
                    result.append((res_code, mfa))
            else:
                result.append((res_code, profile))
        return result
