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
                            "calling aws sts get-caller-identity with "
                            "current profile."),
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
                tmp_client = boto3.client("sts", **self["profile"])
                result.extend(self._handle_err(tmp_client.get_caller_identity,
                                               key="Arn"))
                if result[-1][0] == res.RESULT:
                    self["UserName"] = result.pop()[1].split("/")[-1]
                else:
                    result.append((res.INFO,
                                   ("Cannot retrieve user name."
                                    "But if your specify user name, "
                                    "you might be able to list policies.")))
                    return result
        result.extend(self._handle_err(client.list_attached_user_policies,
                                       UserName=self["UserName"],
                                       key="AttachedPolicies"))
        if result[-1][0] == res.RESULT:
            policies = result.pop()[1]
            result.append((res.GOOD, "You could list attached user policies"))
            for policy in policies:
                policy_arn = policy["PolicyArn"]
                result.extend(self._handle_err(client.list_policy_versions,
                                               PolicyArn=policy_arn,
                                               key="Versions"))
                if result[-1][0] == res.RESULT:
                    versions = result.pop()[1]
                    for version in versions:
                        version_id = version["VersionId"]
                        result.extend(
                            self._handle_err(
                                client.get_policy_version,
                                PolicyArn=policy_arn,
                                VersionId=version_id,
                                key="PolicyVersion"
                            )
                        )
                        if result[-1][0] == res.RESULT:
                            tmp = result.pop()
                            result.append((tmp[0], {
                                "Statement": tmp[1]["Document"]["Statement"],
                            }))
        # Inline policies
        # Need to handle IsTruncated!!!
        kwargs = {"UserName": self["UserName"]}
        is_truncated = True
        marker = ""
        while is_truncated:
            if marker:
                kwargs["Marker"] = marker
            result.extend(
                self._handle_err(
                    client.list_user_policies,
                    **kwargs,
                    # for test
                    # MaxItems=1
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
                            client.get_user_policy,
                            UserName=self["UserName"],
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
