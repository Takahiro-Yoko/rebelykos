import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "get_user_policies"
        self.description = "List user policies"
        self.author = "Takahiro Yokoyama"
        self.options["UserName"] = {
            "Description": ("The name (friendly name, not ARN) of the"
                            " user to list attached policies for. "
                            "if not specified, try to get user name by "
                            "calling get-user or get-caller-identity with"
                            " current profile."),
            "Required": False,
            "Value": ""
        }

    def run(self):
        result = []
        client = boto3.client("iam", **self["profile"])
        if not self["UserName"]:
            result.extend(self._handle_err(client.get_user))
            if result[-1][0] == res.RESULT:
                self["UserName"] = result.pop()[1]["User"]["UserName"]
            else:
                sts_client = boto3.client("sts", **self["profile"])
                result.extend(self._handle_err(sts_client.get_caller_identity,
                                               key="Arn"))
                if result[-1][0] == res.RESULT:
                    self["UserName"] = result.pop()[1].split("/")[-1]
                else:
                    result.append((res.INFO,
                                   ("Cannot retrieve user name."
                                    "But if your specify user name, "
                                    "you might be able to list policies.")))
                    return result
        is_truncated = True
        marker = ""
        kwargs = {"UserName": self["UserName"]}
        while is_truncated:
            if marker:
                kwargs["Marker"] = marker
            result.extend(self._handle_err(client.list_attached_user_policies,
                                           **kwargs))
                                           # **kwargs,
                                           # for test
                                           # MaxItems=1))
            if result[-1][0] == res.RESULT:
                tmp = result.pop()[1]
                result.append((res.GOOD,
                               "You could list attached user policies"))
                is_truncated = tmp.get("IsTruncated")
                marker = tmp["Marker"] if is_truncated else ""
                for policy in tmp["AttachedPolicies"]:
                    _is_truncated = True
                    _marker = ""
                    while _is_truncated:
                        _kwargs = {"PolicyArn": policy["PolicyArn"]}
                        if _marker:
                            _kwargs["Marker"] = _marker
                        result.extend(
                            self._handle_err(client.list_policy_versions,
                                             **_kwargs)
                                             # **_kwargs,
                                             # for test
                                             # MaxItems=1)
                        )
                        if result[-1][0] == res.RESULT:
                            _tmp = result.pop()[1]
                            _is_truncated = _tmp.get("IsTruncated")
                            _marker = _tmp["Marker"] if _is_truncated else ""
                            for version in _tmp["Versions"]:
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
        # Inline policies
        kwargs = {"UserName": self["UserName"]}
        is_truncated = True
        marker = ""
        while is_truncated:
            if marker:
                kwargs["Marker"] = marker
            result.extend(self._handle_err(client.list_user_policies,
                                           **kwargs))
                                           # **kwargs,
                                           # for test
                                           # MaxItems=1))
            if result[-1][0] == res.RESULT:
                tmp = result.pop()[1]
                is_truncated = tmp.get("IsTruncated")
                marker = tmp["Marker"] if is_truncated else ""
                for p in tmp["PolicyNames"]:
                    result.extend(self._handle_err(client.get_user_policy,
                                                   UserName=self["UserName"],
                                                   PolicyName=p,
                                                   key="PolicyDocument"))
                    if result[-1][0] == res.RESULT:
                        result.append((
                            res.RESULT,
                            {"Statement": result.pop()[1]["Statement"]}
                        ))
            else:
                break
        return result
