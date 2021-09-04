import boto3
import botocore

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
        # try:
        if 1 == 1:
            res_code, obj = self._handle_err(client.get_account_summary)
            if res_code == res.RESULT:
                result.append((res.GOOD,
                               "Root key! or IAM access"))
                result.append((res.INFO,
                               "Printing Account Summary"))
                result.append((res.RESULT,
                               obj["SummaryMap"]))
            else:
                result.append((res_code, obj))
            res_code, users = self._handle_err(client.list_users)
            if res_code == res.RESULT:
                result.append((res.INFO, "Printing Users"))
                result.append((res.RESULT, users["Users"]))
            else:
                result.append((res_code, users))

            result.append((res.INFO, "Checking for console access"))
            for user in users["Users"]:
                user = user["UserName"]
                # try:
                if 1 == 1:
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
                # except botocore.exceptions.ClientError as e:
                #     if e.response["Error"]["Code"] == "NoSuchEntity":
                #         result.append((
                #             res.BAD,
                #             f"user: {user} doesn't have console access"
                #         ))
                #     else:
                #         result.append((
                #             res.BAD,
                #             f"Unexpected error: {e}"
                #         ))
        # except botocore.exceptions.ClientError as e:
        #     ecode = e.response["Error"]["Code"]
        #     key = self['profile']['aws_access_key_id']
        #     if ecode == "InvalidClientTokenId":
        #         result.append((res.BAD, "The AWS key is invalid"))
        #     elif ecode == "AccessDenied":
        #         result.append((res.BAD,
        #                        f"{key} : is not a root key"))
        #     elif ecode == "SubscriptionRequiredException":
        #         result.append((
        #             res.BAD, 
        #             (f"{key} : has permissions but isn't signed up for "
        #              "service - usually means you have a root account")
        #         ))
        #     else:
        #         result.append((res.BAD, f"Unexpected error: {e}"))
        return result
