import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "group_info"
        self.description = ("List groups, group policies and"
                            " users belonging to group.")
        self.author = "Takahiro Yokoyama"
        self.options["GroupName"] = {
            "Description": "The Group's name identifier.",
            "Required": False,
            "Value": ""
        }

    def run(self):
        client = boto3.client("iam", **self["profile"])
        if self["GroupName"]:
            group = boto3.resource("iam").Group(self["GroupName"])
            yield res.INFO, "Showing group arn."
            yield res.RESULT, group.arn

            yield res.INFO, "Listing attached policies."
            yield from self._iam_attached_policies(
                client,
                group.attached_policies.all()
            )

            yield res.INFO, "Listing inline policies."
            yield from self._iam_inline_policies(group.policies.all())

            yield (
                res.INFO,
                ("Listing users belonging to"
                 f" group {self['GroupName']}")
            )
            for user in group.users.all():
                yield res.RESULT, user.name
        else:
            for result in self._handle_is_truncated(client.list_groups):
                if result[0] == res.RESULT:
                    groups = result[1]["Groups"]
                    for group in groups:
                        yield res.RESULT, group["GroupName"]
                else:
                    yield result

        yield res.END, "End"
