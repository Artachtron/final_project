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
                            ## Turbo
                            "turbo_threshold": 1.0,
                            "turbo_prob": 0.05,
                            "turbo_factor": 20,
                            ## Link mutation
                            "disable_prob": 0.1,
                            "enable_prob": 0.1,
                            "weight_mutate_power": 0.5,
                            "link_mutate_prob": 0.1,
                            ## Node mutation
                            "node_mutate_prob": 0.1,
                            "mutate_bias_prob": 0.1,
                            ## Add link mutation
                            "new_link_prob": 0.1,
                            "add_link_prob": 0.25,
                            "add_link_tries": 50,
                            ## Add node mutation
                            "add_node_prob": 0.25,
                            # Mating
                            "mate_multipoint_prob": 0.0,
                            # Compatibility
                            "disjoint_coeff": 1.0,
                            "excess_coeff": 1.0,
                            "node_diff_coeff": 0.5,
                            "link_diff_coeff": 0.5,
                            "mutation_difference_coeff": 0.5,
                            "compatibility_threshod": 3.0,
                        },#21

                    "Simulation":{
                        "evaluate": True,
                        # Difficutly
                        "difficulty_max": 10,
                        "difficulty_min": 1,
                        "diffulty_cycles_step": 150,
                        "diffulty_factor_coefficient": 0.1,
                        "difficulty_cycle_factor_threshold": 5000,
                        "difficulty_pop_threshold": 100,
                        "difficulty_pop_factor": 50,
                        "difficulty_pop_coefficient": 0.1,
                        "difficulty_factor": 1.0,
                        "difficulty_level": 1,
                        "max_cycle": 1000,
                        # Grid
                        "grid_width": 40,
                        "grid_height": 40,
                        "block_size": 17,
                        "simulation_speed": 20,
                        # Populate
                        "min_horizontal_size_section": 5,
                        "max_horizontal_size_section": 10,
                        "min_vertical_size_section": 5,
                        "max_vertical_size_section": 10,
                        "animal_sparsity": 1,
                        "spawn_initial_energy": True,
                        "spawn_energy": False,
                        "energy_sparsity": 1,
                        "spawn_energy_frequency":10,
                        "energy_expiry": 10,
                        "energy_quantity": 100,
                        "spawn_tree": False,
                        "tree_sparsity": 5,
                        #26
                        "Entity":{
                            "initial_size": 1,
                            "init_max_age": 10,
                            "init_blue_energy": 100,
                            "init_red_energy": 100,
                            "init_action_cost": 1,
                            "max_age_size_coeff": 10,
                            "growth_energy_required": 40,
                            "child_energy_cost_divisor": 100,
                        }, #8

                        "Animal":{
                            # Animal
                            ## Initial attributes
                            "init_adult_size": 4,
                            "init_blue_energy": 50,
                            "init_red_energy": 0,
                            ## Brain
                            "complete": False,
                            "num_input": 8,
                            "num_output": 6,
                            "num_action": 4,
                            ## Energy
                            "reproduction_cost": 3,
                            "planting_cost": 1,
                            ## Inputs
                            "normal_size": 10,
                            "normal_energy": 1000,
                            "entity_sight_range":5,
                            "energy_sight_range": 3,
                            ## Actions
                            "die_giving_birth_prob": 0.02,
                            "max_number_offsping": 5,
                            "random_action_prob": 0.05,
                            "success_reproduction": 1.00,
                            "incest": False,
                            "reproduction_range": 3,
                            "move_threshold": 0.1,
                            "grow_threshold": 0.5,
                            "reproduction_threshold": 0.5,
                            "plant_threshold": 0.5,
                            "drop_threshold": 0.5,
                            "paint_threshold": 0.5
                        }, #25

                        "Tree":{
                            #Tree
                            ## Initial attributes
                            "init_adult_size": 5,
                            "init_max_age": 20,
                            "init_blue_energy": 100,
                            "init_red_energy": 100,
                            ## Brain
                            "complete": False,
                            "num_tree_input": 6,
                            "num_tree_output": 8,
                            "num_tree_action": 4,
                            ## Inputs
                            "energy_sight_range": 1,
                            "normal_size": 100,
                            "normal_energy": 1000,
                        }, #9
                        "Resource":{
                            "expiry_date": 20 #1
                        }
                    }
                }

class ConfigManager:
    directory = join(
            Path(
                dirname(
                    realpath(__file__))).parent.parent.parent.absolute(),
            "configuration/")

    __instance = None
    def __new__(cls, *args):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls, *args)
        return cls.__instance

    def __init__(self):
        self.parser = parser = optparse.OptionParser()
        group = optparse.OptionGroup(parser, "Settings")
        group.add_option("-c", "--config", dest="my_config_file", help="configuration")
        group.add_option("-l", "--load", dest="load_simulation", help="simulation")
        group.add_option("-d", "--display", action="store_true", dest="display", help="display")
        
        self.settings: Dict[str, Any] = default_settings
        if "pytest" not in sys.modules:
            self.parse_config()

    def parse_config(self):
        opt, args = self.parser.parse_args()
        if opt.my_config_file:
            config_data = json.load(open(join(ConfigManager.directory, opt.my_config_file), encoding="utf-8"))

            for key in config_data:
                for subkey in config_data[key]:
                    if isinstance(config_data[key][subkey], type(dict())):
                        self.settings[key][subkey].update(config_data[key][subkey])

                    else:
                        self.settings[key][subkey] = config_data[key][subkey]


        self.loaded_simulation = opt.load_simulation or None
        self.display = bool(opt.display)


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

        with open(join(ConfigManager.directory,f"config_{config_letter}_{config_num}.json"), "w", encoding="utf-8") as write_file:
            json.dump(settings, write_file, indent=4)

    def set_difficulty(self, new_difficulty):
        new_difficulty *= self.settings['Simulation']['difficulty_factor']
        max_difficulty = self.settings['Simulation']['difficulty_max']
        min_difficulty = self.settings['Simulation']['difficulty_min']
        new_difficulty = min(max(min_difficulty, new_difficulty), max_difficulty)
        self.settings['Simulation']['difficulty_level'] = new_difficulty
        return self.settings['Simulation']['difficulty_level']

    def increment_difficulty_factor(self):
        self.settings['Simulation']['difficulty_factor'] +=  1

    def set_difficulty_factor(self, factor):
        self.settings['Simulation']['difficulty_factor'] = factor

    def set_difficulty_range(self, phase: int):
        self.settings['Simulation']['difficulty_max'] *= phase
        self.settings['Simulation']['difficulty_min'] *= phase
        
    def set_cycle(self, cycle):
        self.settings['Simulation']['cycle'] = cycle

config = ConfigManager()
