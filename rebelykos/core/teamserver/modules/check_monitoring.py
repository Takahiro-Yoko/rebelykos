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
        result = []

        client = boto3.client("cloudtrail", **self["profile"])
        result.extend(self._handle_err(client.describe_trails,
                                       key="trailList",
                                       msg="Describing cloudtrails"))

        client = boto3.client("guardduty", **self["profile"])
        result.extend(self._handle_err(client.list_detectors,
                                       key="DetectorIds",
                                       msg="Listing guadduty"))

        client = boto3.client("accessanalyzer")
        result.extend(self._handle_err(client.list_analyzers,
                                       key="analyzers",
                                       msg="Listing accessanalyzers"))
        return result
