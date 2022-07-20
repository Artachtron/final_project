import json
import optparse
from typing import Dict

default_options = {
                    "NEAT":{
                            "test": 324,
                            "t": 10
                            },
                    "Sim":{
                           "sim": 13
                          }
                    }

class ConfigManager:
    def __init__(self):
        self.parser = parser = optparse.OptionParser()
        group = optparse.OptionGroup(parser, "Common options")
        group.add_option("-c", "--config", dest="my_config_file", help="configuration")

        self.options: Dict[str, int] = default_options
        self.parse_config()

    def parse_config(self):
        opt, args = self.parser.parse_args()

        config_data = json.load(open(opt.my_config_file))
        for key in default_options.keys():
            if key in config_data.keys():
                self.options[key].update(config_data[key])

    def __getitem__(self, key):
        return self.options[key]

config = ConfigManager()
