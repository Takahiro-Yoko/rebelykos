import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "list_roles_and_get_role_policies"
        self.description = ("List all role-names if rolename not specified."
                            " If specified, Describe the role and get "
                            "policies attached to that role.")
        self.author = "Takahiro Yokoyama"
        self.options["rolename"] = {
            "Description": ("Describe role detail and policies"
                            "attached to this role."),
            "Required": False,
            "Value": ""
        }

    def run(self):
        result = []
        client = boto3.client("iam", **self["profile"])
        result.extend(self._handle_err(client.list_roles, key="Roles"))
        if result[-1][0] == res.RESULT:
            roles = result.pop()[1]
            if self["rolename"]:
                roles = [{"Statement": \
                    role["AssumeRolePolicyDocument"]["Statement"],
                          "Arn": role["Arn"]}
                         for role in roles
                         if role["RoleName"] == self["rolename"]]
                roles = roles[0] if roles else roles
            else:
                roles = [role["RoleName"] for role in roles]
            result.append((res.RESULT, roles))
        if self["rolename"]:
            result.extend(
                self._handle_err(
                    client.list_attached_role_policies,
                    RoleName=self["rolename"],
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
