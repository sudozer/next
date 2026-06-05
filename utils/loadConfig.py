import json
from pathlib import Path
import pdb
class Configs():

    def loadGlobalConfig(self):
        #importing CONFIG as this function reloads the config every time it's accessed in case there have been changes
        self.global_config_path = Path(__file__).resolve().parent.parent / 'config' / 'globalConfig.json'
        with open(self.global_config_path) as f:
            config = json.load(f)
        return config
