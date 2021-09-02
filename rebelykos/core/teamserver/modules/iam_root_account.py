import boto3
import botocore

from rebelykos.core.response import Response as res
from rebelykos.core.utils import print_good, print_info, print_bad
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        self.name = "check_root_account"
        self.language = "python"
        self.description = ("Check if the account has root"
                            " or elevated IAM privileges")
        self.author = ""
        self.references = []
        self.options = {
            "profile": {
                "Description": "The profile to use privileges check",
                "Required": True,
                "Value": ""
            }
        }

    def run(self):
        client = boto3.client("iam", **self.options["profile"]["Value"])
        result = []
        try:
            summary = client.get_account_summary()
            if summary:
                result.append((res.GOOD,
                               "Root key! or IAM access"))
                result.append((res.INFO,
                               "Printing Account Summary"))
                result.append((res.RESULT,
                               summary["SummaryMap"]))
            users = client.list_users()
            if users:
                result.append((res.INFO, "Printing Users"))
                result.append((res.RESULT, users["Users"]))

            result.append((res.INFO, "Checking for console access"))
            for user in users["Users"]:
                user = user["UserName"]
                try:
                    profile = client.get_login_profile(UserName=user)
                    if profile:
                        result.append((
                            res.GOOD, 
                            (f"User {user} likely has console access"
                             " and the password can be reset :-)")
                        ))
                        result.append((res.INFO,
                                       "Checking for MFA on account"))
                        mfa = client.list_mfa_devices(UserName=user)
                        result.append((res.INFO, mfa["MFADevices"]))
                except botocore.exceptions.ClientError as e:
                    if e.response["Error"]["Code"] == "NoSuchEntity":
                        result.append((
                            res.BAD,
                            f"user: {user} doesn't have console access"
                        ))
                    else:
                        result.append((
                            res.BAD,
                            f"Unexpected error: {e}"
                        ))
        except botocore.exceptions.ClientError as e:
            ecode = e.response["Error"]["Code"]
            key = self.options['profile']['Value']['aws_access_key_id']
            if ecode == "InvalidClientTokenId":
                result.append((res.BAD, "The AWS key is invalid"))
            elif ecode == "AccessDenied":
                result.append((res.BAD,
                               f"{key} : is not a root key"))
            elif ecode == "SubscriptionRequiredException":
                result.append((
                    res.BAD, 
                    (f"{key} : has permissions but isn't signed up for "
                     "service - usually means you have a root account")
                ))
            else:
                result.append((res.BAD, f"Unexpected error: {e}"))
        return result
