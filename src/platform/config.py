import json
import optparse
from typing import Dict

# Network structures
        num_inputs: int = 96,
        num_outputs: int = 12,



default_options = {
                    "NEAT":{
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
                        "grid_width": 20,
                        "grid_height": 20,
                        
                        "Animal":{
                            # Animal
                            ## Initial attributes
                            "init_adult_size": 5,
                            ## Brain
                            "num_input": 96,
                            "num_output": 15,
                            "num_action": 8, 
                            ## Energy
                            "reproduction_cost": 10,
                            "planting_cost": 10,
                            ## Inputs
                            "normal_size": 100,
                            "normal_energy": 100000,
                            ## Actions
                            "die_giving_birth_prob": 0.02,
                        },
                        
                        "Tree":{    
                            #Tree
                            ## Brain
                            "num_tree_input": 88,
                            "num_tree_output" 8,
                            "num_tree_action": 4,
                            ## Inputs
                            "normal_size": 100,
                            "normal_energy": 100000,
                        }                             
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
