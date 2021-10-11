import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "check_monitoring"
        self.description = ("Check whether CloudTrail, GuadDuty"
                            " and Access Analyzer are running.")
        self.author = "Takahiro Yokoyama"

    def run(self):
        client = boto3.client("cloudtrail", **self["profile"])
        func_info, result = self._handle_err(client.describe_trails)
        yield func_info
        if result[0] == res.RESULT:
            yield result[0], result[1]["trailList"]
        else:
            yield result

        client = boto3.client("guardduty", **self["profile"])
        func_info, result = self._handle_err(client.list_detectors)
        yield func_info
        if result[0] == res.RESULT:
            yield result[0], result[1]["DetectorIds"]
        else:
            yield result

        client = boto3.client("accessanalyzer")
        func_info, result = self._handle_err(client.list_analyzers)
        yield func_info
        if result[0] == res.RESULT:
            yield result[0], result[1]["analyzers"]
        else:
            yield result

        yield res.END, "End"
