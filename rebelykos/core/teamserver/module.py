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

    def _handle_err(self, func, **kwargs):
        try:
            return res.RESULT, func(**kwargs)
        except botocore.exceptions.ClientError as e:
            # func_args = f"{'(' + str(kwargs) + ')' if kwargs else ''}"
            func_args = f"({kwargs or ''})"
            return res.BAD, (f'When calling {func.__name__}'
                             f'{func_args}: {e.response["Error"]["Code"]}')
            # ecode = e.response["Error"]["Code"]
            # key = self['profile']['aws_access_key_id']
            # if ecode == "InvalidClientTokenId":
            #     msg = f"{func}: The AWS key is invalid"
            # elif ecode == "AccessDenied":
            #     msg = f"{func}: AccessDenied"
            # elif ecode == "SubscriptionRequiredException":
            #     msg = (f"{key} : has permissions but isn't signed up for"
            #            " service - usually means you have a root account")
            # else:
            #     msg = f"{func}: Unexpected error ({e})"
            # return res.BAD, msg


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
