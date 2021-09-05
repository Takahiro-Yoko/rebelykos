import botocore

from rebelykos.core.response import Response as res

class Module:
    def __init__(self):
        self.name = ""
        self.language = ""
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

    def _handle_err(self, func, key=None, msg=None, **kwargs):
        try:
            func_result = func(**kwargs)[key] if key else func(**kwargs)
            msgs = []
            if msg:
                msgs.append((res.GOOD, msg))
            msgs.append((res.INFO, f"{func.__name__}({kwargs or ''})"))
            msgs.append((res.RESULT, func_result))
            return msgs
        except botocore.exceptions.ClientError as e:
            return [(res.BAD, (f'When calling {func.__name__}({kwargs or ""})'
                               f': {e.response["Error"]["Code"]}'))]

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
