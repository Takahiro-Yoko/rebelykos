import os
import tempfile
import zipfile

import botocore

from rebelykos.core.response import Response as res
from rebelykos.core.utils import gen_random_string


class Module:
    def __init__(self):
        self.name = ""
        # Currently all modules written in Python3
        self.language = "Python"
        self.description = ""
        self.author = ""
        self.references = []
        # Currently all modules using profile
        self.options = {
            "profile": {
                "Description": "The profile to use module",
                "Required": True,
                "Value": ""
            }
        }

    def _handle_err(self, func, **kwargs):
        func_info = (res.INFO, f"{func.__name__}({kwargs or ''})")
        try:
            func_result = func(**kwargs)
        except botocore.exceptions.ClientError as e:
            return func_info, (res.BAD, e.response["Error"]["Code"])
        else:
            return func_info, (res.RESULT, func_result)

    def _handle_is_truncated(self, func, **kwargs):
        is_truncated = True
        marker = ""
        while is_truncated:
            if marker:
                kwargs["Marker"] = marker
            elif "Marker" in kwargs:
                del kwargs["Marker"]
            func_info, result = self._handle_err(
                func,
                **kwargs
            )
            yield func_info
            if result[0] == res.RESULT:
                is_truncated = result[1].get("IsTruncated")
                marker = result[1]["Marker"] if is_truncated else ""
                yield result
            else:
                yield result
                break

    def _iam_attached_policies(self, client, policies):
        for policy in policies:
            for result in self._handle_is_truncated(
                    client.list_policy_versions,
                    PolicyArn=policy.arn
                    ):
                if result[0] == res.RESULT:
                    versions = result[1]["Versions"]
                    for version in versions:
                        func_info, result = self._handle_err(
                            client.get_policy_version,
                            PolicyArn=policy.arn,
                            VersionId=version["VersionId"]
                        )
                        yield func_info
                        if result[0] == res.RESULT:
                            doc = result[1]["PolicyVersion"]["Document"]
                            yield (
                                res.RESULT,
                                {"Statement": doc["Statement"]}
                            )
                        else:
                            yield result
                else:
                    yield result

    def _iam_inline_policies(self, policies):
        for policy in policies:
            yield (res.RESULT,
                   {"PolicyName": policy.policy_name,
                    "Statement": policy.policy_document["Statement"]})

    def _lambda_privesc(self, lambda_privesc, role, client):
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
                    Role=role,
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

    def __getitem__(self, key):
        for k, v in self.options.items():
            if k.lower() == key.lower():
                return v["Value"]

    def __setitem__(self, key, value):
        for k, _ in self.options.items():
            if k.lower() == key.lower():
                self.options[k]["Value"] = value

    def __iter__(self):
        yield ("name", self.name)
        yield ("language", self.language)
        yield ("description", self.description)
        yield ("author", self.author)
        yield ("references", self.references)
        yield ("options", self.options)
