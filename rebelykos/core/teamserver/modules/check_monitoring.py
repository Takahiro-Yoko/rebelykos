import boto3
import botocore

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "check_monitoring"
        self.language = "Python"
        self.description = ("Check whether CloudTrail, GuadDuty"
                            " or Access Analyzer runnig")
        self.author = "Takahiro Yokoyama"

    def run(self):
        client = boto3.client("cloudtrail", **self["profile"])
        res_code, obj = self._handle_err(client.describe_trails)
        result = []
        if res_code == res.RESULT:
            result.append((res.GOOD,
                           "You have right to describe cloudtrails!"))
            result.append((res.INFO, "Describing cloudtrails"))
            result.append((res_code, obj["trailList"]))
        else:
            result.append((res_code, obj))
        return result
