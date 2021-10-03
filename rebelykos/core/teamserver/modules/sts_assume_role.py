import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.db import RLDatabase
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "assume_role"
        self.description = ("Run sts assume-role and register this "
                            "new generated credentials to database.")
        self.author = "Takahiro Yokoyama"
        self.options["RoleArn"] = {
            "Description": ("The Amazon Resource Name (ARN)"
                            " of the role to assume."),
            "Required": True,
            "Value": ""
        }
        self.options["RoleSessionName"] = {
            "Description": ("An identifier for the assumed role session."
                            " if already used this name in profile database"
                            ", then update credentials about that profile."),
            "Required": True,
            "Value": ""
        }

    def run(self):
        client = boto3.client("sts", **self["profile"])
        func_info, result = self._handle_err(
            client.assume_role,
            RoleArn=self["RoleArn"],
            RoleSessionName=self["RoleSessionName"]
        )
        yield func_info
        if result[0] == res.RESULT:
            creds = result[1]["Credentials"]
            yield res.GOOD, "Successfully assume role"
            new_profile = {
                "profile": self["RoleSessionName"],
                "access_key_id": creds["AccessKeyId"],
                "secret_access_key": creds["SecretAccessKey"],
                "session_token": creds["SessionToken"],
                "region": self["profile"]["region_name"]
            }
            with RLDatabase() as db:
                db.upsert(new_profile)
                yield res.INFO, "Add generated credentials information"
                yield res.RESULT, new_profile
        else:
            yield result
        yield res.END, "End"
