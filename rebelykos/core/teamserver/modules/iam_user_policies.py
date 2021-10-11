import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "user_policies"
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

        # Get UserName
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

        user = boto3.resource("iam").User(self["UserName"])
        yield res.INFO, "Listing attached policies."
        yield from self._iam_attached_policies(
            client,
            user.attached_policies.all()
        )
                    
        yield res.INFO, "Listing inline policies."
        yield from self._iam_inline_policies(user.policies.all())

        yield res.END, "End"
