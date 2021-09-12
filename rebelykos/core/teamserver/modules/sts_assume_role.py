import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.db import RLDatabase
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "assume_role"
        self.description = ("run sts assume-role and register this "
                            "new generated credentials to database.")
        self.author = "Takahiro Yokoyama"
        self.options["rolearn"] = {
            "Description": ("The Amazon Resource Name (ARN)"
                            " of the role to assume."),
            "Required": True,
            "Value": ""
        }
        self.options["rolesessionname"] = {
            "Description": ("An identifier for the assumed role session."
                            " if already used this name in profile database"
                            ", then update credentials about that profile."),
            "Required": True,
            "Value": ""
        }

    def run(self):
        result = []
        client = boto3.client("sts", **self["profile"])
        result.extend(
            self._handle_err(
                client.assume_role,
                RoleArn=self["rolearn"],
                RoleSessionName=self["rolesessionname"]
            )
        )
        if result[-1][0] == res.RESULT:
            result.append((res.GOOD, "Successfully assume role"))
            creds = result.pop()[1]["Credentials"]
            new_profile = {
                "profile": self["rolesessionname"],
                "access_key_id": creds["AccessKeyId"],
                "secret_access_key": creds["SecretAccessKey"],
                "session_token": creds["SessionToken"],
                "region": self["profile"]["region_name"]
            }
            with RLDatabase() as db:
                db.upsert(new_profile)
                result.append((res.INFO,
                               "Add generated credentials information"))
                result.append((res.RESULT, new_profile))
        return result
