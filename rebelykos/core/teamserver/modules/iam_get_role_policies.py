import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "get_role_policies"
        self.description = "Get policies attached to role"
        self.author = "Takahiro Yokoyama"
        self.options["role"] = {
            "Description": "Get policies attached to this role",
            "Required": True,
            "Value": ""
        }

    def run(self):
        result = []
        client = boto3.client("iam", **self["profile"])
        result.extend(
            self._handle_err(
                client.list_attached_role_policies,
                RoleName=self["role"],
                key="AttachedPolicies"
            )
        )
        if result[-1][0] == res.RESULT:
            policies = result.pop()[1]
            for policy in policies:
                result.extend(
                    self._handle_err(
                        client.list_policy_versions,
                        PolicyArn=policy["PolicyArn"],
                        key="Versions"
                    )
                )
                if result[-1][0] == res.RESULT:
                    versions = result.pop()[1]
                    for version in versions:
                        result.extend(
                            self._handle_err(
                                client.get_policy_version,
                                PolicyArn=policy["PolicyArn"],
                                VersionId=version["VersionId"],
                                key="PolicyVersion"
                            )
                        )
                        if result[-1][0] == res.RESULT:
                            tmp = result.pop()
                            result.append((tmp[0], {
                                "Statement": \
                                    tmp[1]["Document"]["Statement"]
                            }))
        return result
