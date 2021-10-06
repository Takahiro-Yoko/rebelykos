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
        client = boto3.client("iam", **self["profile"])
        if not self["UserName"]:
            func_info, result = self._handle_err(client.get_user)
            yield func_info
            if result[0] == res.RESULT:
                self["UserName"] = result[1]["User"]["UserName"]
                yield res.RESULT, self["UserName"]
            else:
                yield result
                sts_client = boto3.client("sts", **self["profile"])
                func_info, result = self._handle_err(
                    sts_client.get_caller_identity
                )
                yield func_info
                if result[0] == res.RESULT:
                    self["UserName"] = result[1]["Arn"].split("/")[-1]
                    yield res.RESULT, self["UserName"]
                else:
                    yield result
                    yield (res.INFO,
                           ("Cannot retrieve user name. "
                            "But if your specify user name, "
                            "you might be able to list policies."))
                    yield res.END, "End"
        is_truncated = True
        marker = ""
        kwargs = {"UserName": self["UserName"]}
        while is_truncated:
            if marker:
                kwargs["Marker"] = marker
            func_info, result = self._handle_err(
                client.list_attached_user_policies,
                **kwargs
            )
                # for test
                # **kwargs,
                # MaxItems=1
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
                            # for test
                            # **_kwargs,
                            # MaxItems=1
                        # )
                        yield func_info
                        if result[0] == res.RESULT:
                            _is_truncated = result[1].get("IsTruncated")
                            _marker = result[1]["Marker"] \
                                    if _is_truncated else ""
                            versions = result[1]["Versions"]
                            for version in versions:
                                func_info, result = self._handle_err(
                                    client.get_policy_version,
                                    PolicyArn=policy["PolicyArn"],
                                    VersionId=version["VersionId"],
                                )
                                yield func_info
                                if result[0] == res.RESULT:
                                    policy_ver = result[1]["PolicyVersion"]
                                    doc = policy_ver["Document"]
                                    yield (res.RESULT, 
                                           {"Statement": doc["Statement"]})
                        else:
                            yield result
                            break
            else:
                yield result
                break
        # Inline policies
        kwargs = {"UserName": self["UserName"]}
        is_truncated = True
        marker = ""
        while is_truncated:
            if marker:
                kwargs["Marker"] = marker
            func_info, result = self._handle_err(client.list_user_policies,
                                                 **kwargs)
                                                 # for test
                                                 # **kwargs,
                                                 # MaxItems=1)
            yield func_info
            if result[0] == res.RESULT:
                is_truncated = result[1].get("IsTruncated")
                marker = result[1]["Marker"] if is_truncated else ""
                policy_names = result[1]["PolicyNames"]
                for p in policy_names:
                    func_info, result = self._handle_err(
                        client.get_user_policy,
                        UserName=self["UserName"],
                        PolicyName=p,
                    )
                    yield func_info
                    if result[0] == res.RESULT:
                        yield (
                            res.RESULT,
                            {"Statement": \
                                    result[1]["PolicyDocument"]["Statement"]}
                        )
                    else:
                        yield result
            else:
                yield result
                break
        yield res.END, "End"
