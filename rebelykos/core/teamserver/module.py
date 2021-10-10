import botocore

from rebelykos.core.response import Response as res

class Module:
    def __init__(self):
        self.name = ""
        # Currently all module written in Python3
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
