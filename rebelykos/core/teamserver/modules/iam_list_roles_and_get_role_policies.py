import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "list_roles_and_get_role_policies"
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
        is_truncated = True
        marker = ""
        kwargs = {}
        while is_truncated:
            if marker:
                kwargs["Marker"] = marker
            func_info, result = self._handle_err(client.list_roles,
                                                 **kwargs)
                                                 # for test
                                                 # **kwargs,
                                                 # MaxItems=1)
            yield func_info
            if result[0] == res.RESULT:
                is_truncated = result[1].get("IsTruncated")
                marker = result[1]["Marker"] if is_truncated else ""
                if self["RoleName"]:
                    for role in result[1]["Roles"]:
                        if role["RoleName"] == self["RoleName"]:
                            policy_doc = role["AssumeRolePolicyDocument"]
                            yield (
                                result[0],
                                {"Statement": policy_doc["Statement"],
                                 "Arn": role["Arn"]}
                            )
                            is_truncated = False
                            break
                else:
                    for role in result[1]["Roles"]:
                        yield res.RESULT, role["RoleName"]
            else:
                yield result
                break
        if self["RoleName"]:
            is_truncated = True
            marker = ""
            kwargs = {"RoleName": self["RoleName"]}
            while is_truncated:
                if marker:
                    kwargs["Marker"] = marker
                func_info, result = self._handle_err(
                    client.list_attached_role_policies,
                    **kwargs
                )
                #     for test
                #     **kwargs,
                #     MaxItems=1
                # )
                yield func_info
                if result[0] == res.RESULT:
                    is_truncated = result[1].get("IsTruncated")
                    marker = result[1]["Marker"] if is_truncated else ""
                    policies = result[1]["AttachedPolicies"]
                    for policy in policies:
                        _is_truncated = True
                        _marker = ""
                        while _is_truncated:
                            _kwargs = {"PolicyArn": policy["PolicyArn"]}
                            if _marker:
                                _kwargs["Marker"] = _marker
                            func_info, result = self._handle_err(
                                client.list_policy_versions,
                                **_kwargs
                            )
                            #     for test
                            #     **_kwargs,
                            #     MaxItems=1
                            # )
                            yield func_info
                            if result[0] == res.RESULT:
                                _is_truncated = result[1].get("IsTruncated")
                                if _is_truncated:
                                    _marker = result[1]["Marker"]
                                versions = result[1]["Versions"]
                                for version in versions:
                                    func_info, result = self._handle_err(
                                        client.get_policy_version,
                                        PolicyArn=policy["PolicyArn"],
                                        VersionId=version["VersionId"],
                                    )
                                    yield func_info
                                    if result[0] == res.RESULT:
                                        p_ver = result[1]["PolicyVersion"]
                                        doc = p_ver["Document"] 
                                        yield (
                                            res.RESULT,
                                            {"Statement": doc["Statement"]}
                                        )
                            else:
                                yield result
                                break
                else:
                    yield result
                    break
            # inline policy
            is_truncated = True
            marker = ""
            kwargs = {"RoleName": self["RoleName"]}
            while is_truncated:
                if marker:
                    kwargs["Marker"] = marker
                func_info, result = self._handle_err(
                    client.list_role_policies,
                    **kwargs
                )
                #     for test
                #     **kwargs,
                #     MaxItems=1
                # )
                if result[0] == res.RESULT:
                    is_truncated = result[1].get("IsTruncated")
                    marker = result[1]["Marker"] if is_truncated else ""
                    policy_names = result[1]["PolicyNames"]
                    for p in policy_names:
                        func_info, result = self._handle_err(
                            client.get_role_policy,
                            RoleName=self["RoleName"],
                            PolicyName=p,
                        )
                        if result[0] == res.RESULT:
                            doc =  result[1]["PolicyDocument"]
                            yield res.RESULT, {"Statement": doc["Statement"]}
                else:
                    yield result
                    break
        yield res.END, "End"
