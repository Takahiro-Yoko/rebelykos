import importlib
import os


class Loader:
    def __init__(self, type="module", paths=[]):
        self.type = type
        self.paths = paths
        self.loaded = []

        self.get_loadables()

    def load(self, path):
        module_spec = importlib.util.spec_from_file_location(self.type, path)
        print(module_spec)
        module = importlib.util.module_from_spec(module_spec)
        print(module)
        module_spec.loader.exec_module(module)
        return module

    def get_loadables(self):
        self.loaded = []
        for path in self.paths:
            for module in os.listdir(path):
                if module[-3:] == ".py" and \
                        not module.startswith("example") and \
                        module != "__init__.py":
                    try:
                        m = self.load(os.path.join(path, module))
                        if self.type == 'listener':
                            self.loaded.append(m.RLListener())
                        elif self.type == "module":
                            self.loaded.append(m.RLModule())
                        elif self.type == "stager":
                            self.loaded.append(m.RLStager())
                    except Exception as e:
                        logging.error(f"Failed loading {self.type} "
                                      f"{os.path.join(path, module)}: {e}")

        logging.debug(f"Loaded {len(self.loaded)} {self.type}(s)")
        return self.loaded
