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
