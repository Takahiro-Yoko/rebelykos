import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "restore_cloudtrail"
        self.description = ("Make IncludeGlobalServiceEvents"
                            " and IsMultiRegionTrail True.")
        self.author = "Takahiro Yokoyama"
        self.options["Name"] = {
            "Description": ("Name of the trail to restore. "
                            "if not specified, try to restore"
                            " all trails user could list."),
            "Required": False,
            "Value": ""
        }

    def run(self):

        def _restore(name):
            result.extend(self._handle_err(client.update_trail,
                                           msg="Successfully restore trail!",
                                           Name=name,
                                           IncludeGlobalServiceEvents=True,
                                           IsMultiRegionTrail=True))

        result = []
        client = boto3.client("cloudtrail", **self["profile"])

        if self["Name"]:
            _restore(self["Name"])
        else:
            result.extend(self._handle_err(client.describe_trails,
                                           key="trailList"))
            if result[-1][0] == res.RESULT:
                trails = result[-1][1]
                for trail in trails:
                    _restore(trail["Name"])
            else:
                result.append((res.INFO,
                               ("Lack of right to list trails "
                                "but might be able to restore trail"
                                " if you specify trail name")))
        return result

