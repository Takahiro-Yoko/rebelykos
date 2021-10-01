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
            return self._handle_err(client.update_trail,
                                    Name=name,
                                    IncludeGlobalServiceEvents=True,
                                    IsMultiRegionTrail=True)

        client = boto3.client("cloudtrail", **self["profile"])

        if self["Name"]:
            func_info, result = _restore(self["Name"])
            yield func_info
            yield result
        else:
            func_info, result = self._handle_err(client.describe_trails)
            yield func_info
            if result[0] == res.RESULT:
                trails = result[1]["trailList"]
                yield result[0], trails
                for trail in trails:
                    func_info, result = _restore(trail["Name"])
                    yield func_info
                    yield result
            else:
                yield (res.INFO,
                       ("Lack of right to list trails "
                        "but might be able to restore trail"
                        " if you specify trail name"))
        yield res.END, "End"

