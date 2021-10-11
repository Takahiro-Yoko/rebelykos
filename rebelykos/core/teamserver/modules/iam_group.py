import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "group_info"
        self.description = "List groups and group policies"
        self.author = "Takahiro Yokoyama"
        self.options["GroupName"] = {
            "Description": "The Group's name identifier.",
            "Required": False,
            "Value": ""
        }

    def run(self):
        client = boto3.client("iam", **self["profile"])
        if self["GroupName"]:
            group = boto3.resource("iam").Group(self["GroupName"])
            yield res.INFO, "Showing group arn."
            yield res.RESULT, group.arn

            yield res.INFO, "Listing attached policies."
            for policy in group.attached_policies.all():
                for result in self._handle_is_truncated(
                        client.list_policy_versions,
                        PolicyArn=policy.arn
                        ):
                    if result[0] == res.RESULT:
                        versions = result[1]["Versions"]
                        for version in versions:
                            func_info, result = self._handle_err(
                                client.get_policy_version,
                                PolicyArn=policy.arn,
                                VersionId=version["VersionId"]
                            )
                            yield func_info
                            if result[0] == res.RESULT:
                                doc = result[1]["PolicyVersion"]["Document"]
                                yield (
                                    res.RESULT,
                                    {"Statement": doc["Statement"]}
                                )
                            else:
                                yield result
                    else:
                        yield result

            yield res.INFO, "Listing inline policies."
            for policy in group.policies.all():
                yield (
                    res.RESULT,
                    {"PolicyName": policy.policy_name,
                     "Statement": policy.policy_document["Statement"]}
                )

            yield (
                res.INFO,
                ("Listing users belonging to"
                 f" group {self['GroupName']}")
            )
            for user in group.users.all():
                yield res.RESULT, user.name
        else:
            for result in self._handle_is_truncated(client.list_groups):
                if result[0] == res.RESULT:
                    groups = result[1]["Groups"]
                    for group in groups:
                        yield res.RESULT, group["GroupName"]
                else:
                    yield result
        yield res.END, "End"
