import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "role_info"
        self.description = ("List all RoleNames if RoleName not specified."
                            " If specified, Describe the role and get "
                            "policies attached to that role.")
        self.author = "Takahiro Yokoyama"
        self.options["RoleName"] = {
            "Description": ("Describe role detail and policies"
                            " attached to this role."),
            "Required": False,
            "Value": ""
        }

    def run(self):
        client = boto3.client("iam", **self["profile"])
        if self["RoleName"]:
            role = boto3.resource("iam").Role(self["RoleName"])
            yield (res.INFO,
                   "Showing role arn and assume_role_policy_document.")
            yield (
                res.RESULT,
                {"Arn": role.arn,
                 "Statement": role.assume_role_policy_document["Statement"]}
            )

            yield res.INFO, "Listing attached policies."
            yield from self._iam_attached_policies(
                client,
                role.attached_policies.all()
            )

            yield res.INFO, "Listing inline policies."
            yield from self._iam_inline_policies(role.policies.all())

        elif not self["RoleName"]:
            for result in self._handle_is_truncated(client.list_roles):
                if result[0] == res.RESULT:
                    for role in result[1]["Roles"]:
                        yield res.RESULT, role["RoleName"]
                else:
                    yield result

        yield res.END, "End"
