import json

from rebelykos.core.utils import gen_random_string


class Job:
    def __init__(self, cmd=None, module=None):
        self.id = gen_random_string()
        self.status = "initialized"
        self.cmd = cmd
        self.module = module

    def payload(self):
        payload = {"id": self.id}

        if self.cmd:
            payload["cmd"] = self.cmd[0]
            payload["args"] = {"args": self.command[1]}
        elif self.modules:
            payload["cmd"] = "CompileAndRun"
            payload["args"] = {
                "source": self.module.payload(),
                "references": self.module.references,
                "run_in_thread": self.module.run_in_thread \
                        if hasattr(self.module, "run_in_thread") else True
            }
        return json.dumps(payload).encode()

    def __repr__(self):
        return (f"<Job id:{self.id} status:{self.status} "
                f"command:{self.cmd} module:{self.module}>")
