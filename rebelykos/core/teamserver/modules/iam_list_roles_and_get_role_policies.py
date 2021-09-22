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
        self.options["RoleName"] = {
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
            if self["RoleName"]:
                roles = [{"Statement": \
                    role["AssumeRolePolicyDocument"]["Statement"],
                          "Arn": role["Arn"]}
                         for role in roles
                         if role["RoleName"] == self["RoleName"]]
                roles = roles[0] if roles else roles
            else:
                roles = [role["RoleName"] for role in roles]
            result.append((res.RESULT, roles))
        if self["RoleName"]:
            is_truncated = True
            marker = ""
            kwargs = {"RoleName": self["RoleName"]}
            while is_truncated:
                if marker:
                    kwargs["Marker"] = marker
                result.extend(
                    self._handle_err(
                        client.list_attached_role_policies,
                        **kwargs,
                        MaxItems=1
                        # RoleName=self["RoleName"],
                        # key="AttachedPolicies"
                    )
                )
                if result[-1][0] == res.RESULT:
                    tmp = result.pop()[1]
                    is_truncated = tmp.get("IsTruncated")
                    if is_truncated:
                        marker = tmp["Marker"]
                    policies = tmp["AttachedPolicies"]
                    for policy in policies:
                        _is_truncated = True
                        _marker = ""
                        while _is_truncated:
                            _kwargs = {"PolicyArn": policy["PolicyArn"]}
                            if _marker:
                                _kwargs["Marker"] = _marker
                            result.extend(
                                self._handle_err(
                                    client.list_policy_versions,
                                    **_kwargs,
                                    MaxItems=1
                                    # PolicyArn=policy["PolicyArn"],
                                    # key="Versions"
                                )
                            )
                            if result[-1][0] == res.RESULT:
                                _tmp = result.pop()[1]
                                _is_truncated = _tmp.get("IsTruncated")
                                if _is_truncated:
                                    _marker = _tmp["Marker"]
                                versions = _tmp["Versions"]
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
                                        doc = result.pop()[1]["Document"]
                                        result.append((
                                            res.RESULT,
                                            {"Statement": doc["Statement"]}
                                        ))
                            else:
                                break
                else:
                    break
            # inline policy
            # Need to handle IsTruncated!!!
            is_truncated = True
            marker = ""
            kwargs = {"RoleName": self["RoleName"]}
            while is_truncated:
                if marker:
                    kwargs["Marker"] = marker
                result.extend(
                    self._handle_err(
                        client.list_role_policies,
                        **kwargs,
                        MaxItems=1
                        # RoleName=self["RoleName"],
                        # key="PolicyNames"
                    )
                )
                if result[-1][0] == res.RESULT:
                    tmp = result.pop()[1]
                    is_truncated = tmp.get("IsTruncated")
                    if is_truncated:
                        marker = tmp["Marker"]
                    inline_policies = tmp["PolicyNames"]
                    for p in inline_policies:
                        result.extend(
                            self._handle_err(
                                client.get_role_policy,
                                RoleName=self["RoleName"],
                                PolicyName=p,
                                key="PolicyDocument"
                            )
                        )
                        if result[-1][0] == res.RESULT:
                            tmp = result.pop()[1]
                            result.append((res.RESULT,
                                           {"Statement": tmp["Statement"]}))
                else:
                    break
        return result
