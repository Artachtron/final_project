import copy
import json
import optparse
import sys
from os.path import dirname, join, realpath
from pathlib import Path
from typing import Any, Dict, Optional

default_settings = {
                    "Run":{
                        "parameter": "",
                        "variation": 0,
                        "run": 0,
                    },

                    "Log":{
                        "resources": False,
                        "death": False,
                        "birth": False,
                        "grid_resources": False,
                        "grid_entities": False,
                        },

                    "NEAT":{
                            #Genome
                            ## genesis
                            "skip_connection": 0.75,
                            # Mutations
                            ## Link mutation
                            "disable_prob": 0.05,
                            "enable_prob": 0.1,
                            "weight_mutate_power": 0.5,
                            "link_mutate_prob": 0.1,
                            ## Node mutation
                            "node_mutate_prob": 0.1,
                            "mutate_bias_prob": 0.1,
                            ## Add link mutation
                            "new_link_prob": 0.1,
                            "add_link_prob": 0.05,
                            "add_link_tries": 20,
                            ## Add node mutation
                            "add_node_prob": 0.02,
                            # Mating
                            "mate_multipoint_prob": 0.0,
                            # Compatibility
                            "disjoint_coeff": 1.0,
                            "excess_coeff": 1.0,
                            "node_diff_coeff": 0.5,
                            "link_diff_coeff": 0.5,
                            "mutation_difference_coeff": 0.5,
                            "compatibility_threshod": 3.0,
                        },

                    "Simulation":{
                        # Difficutly
                        "difficulty_max": 10,
                        "diffulty_cycles_step": 100,
                        "difficulty_pop_threshold": 200,
                        "difficulty_pop_factor": 50,
                        "difficulty_factor": 0.5,
                        "difficulty_level": 1,
                        "max_cycle": 1000,
                        # Grid
                        "grid_width": 50,
                        "grid_height": 50,
                        "block_size": 17,
                        "simulation_speed": 20,
                        # Populate
                        "min_horizontal_size_section": 5,
                        "max_horizontal_size_section": 10,
                        "min_vertical_size_section": 5,
                        "max_vertical_size_section": 10,
                        "animal_sparsity": 5,

                        "Entity":{
                            "initial_size": 10,
                            "init_blue_energy": 100,
                            "init_red_energy": 100,
                            "init_action_cost": 1,
                            "max_age_size_coeff": 5,
                            "growth_energy_required": 10,
                            "child_energy_cost_divisor": 2,
                        },

                        "Animal":{
                            # Animal
                            ## Initial attributes
                            "init_adult_size": 5,
                            "init_blue_energy": 1000,
                            "init_red_energy": 1000,
                            ## Brain
                            "complete": False,
                            "num_input": 96,
                            "num_output": 15,
                            "num_action": 8,
                            ## Energy
                            "reproduction_cost": 10,
                            "planting_cost": 10,
                            ## Inputs
                            "normal_size": 100,
                            "normal_energy": 10000,
                            ## Actions
                            "die_giving_birth_prob": 0.02,
                        },

                        "Tree":{
                            #Tree
                            ## Initial attributes
                            "init_adult_size": 5,
                            "init_blue_energy": 100,
                            "init_red_energy": 100,
                            ## Brain
                            "complete": False,
                            "num_tree_input": 88,
                            "num_tree_output": 8,
                            "num_tree_action": 4,
                            ## Inputs
                            "normal_size": 100,
                            "normal_energy": 10000,
                        }
                    }
                }

class ConfigManager:
    directory = join(
            Path(
                dirname(
                    realpath(__file__))).parent.parent.parent.absolute(),
            "configuration/")

    def __init__(self):
        self.parser = parser = optparse.OptionParser()
        group = optparse.OptionGroup(parser, "Settings")
        group.add_option("-c", "--config", dest="my_config_file", help="configuration")
        group.add_option("-l", "--load", dest="load_simulation", help="simulation")

        self.settings: Dict[str, Any] = default_settings
        if "pytest" not in sys.modules:
            self.parse_config()

    def parse_config(self):
        opt, args = self.parser.parse_args()
        if opt.my_config_file:
            config_data = json.load(open(join(ConfigManager.directory, opt.my_config_file)))

            for key in config_data:
                for subkey in config_data[key]:
                    if isinstance(config_data[key][subkey], type(dict())):
                        self.settings[key][subkey].update(config_data[key][subkey])

                    else:
                        self.settings[key][subkey] = config_data[key][subkey]


        self.loaded_simulation = opt.load_simulation or None
        

    def __getitem__(self, key):
        return self.settings[key]

    @staticmethod
    def write_config(configs: Dict, config_num: int, config_letter: Optional[str]=None) -> None:

        settings = copy.deepcopy(default_settings)

        for key in default_settings:
            if key in configs.keys():
                for subkey in configs[key]:
                    if type(settings[key][subkey]) == type(dict()):
                        settings[key][subkey].update(configs[key][subkey])

                    else:
                        settings[key].update(configs[key])

        with open(join(ConfigManager.directory,f"config_{config_letter}_{config_num}.json"), "w") as write_file:
            json.dump(settings, write_file, indent=4)
            
    def set_difficulty(self, new_difficulty):
        new_difficulty *= self.settings['Simulation']['difficulty_factor']
        max_difficulty = self.settings['Simulation']['difficulty_max']
        new_difficulty = int(min(max(1, new_difficulty), max_difficulty))
        self.settings['Simulation']['difficulty_level'] = new_difficulty
        return self.settings['Simulation']['difficulty_level']
    
    def increment_difficulty_factor(self):
        self.settings['Simulation']['difficulty_factor'] +=  1

config = ConfigManager()
