from typing import Optional

from .config import ConfigManager


def create_config(name: str, value: int, variation: int,
                  category: str, subcategory: Optional[str]=None
                  ):
    configs = dict()
    configs['Run'] = dict()
    configs['Run']['parameter'] = name
    configs['Run']['variation'] = variation
    configs['Run']['value'] = value
    configs[category] = dict()
    if subcategory:
        configs[category][subcategory] = dict()
        configs[category][subcategory][name] = value
    else:
        configs[category][name] = value

    ConfigManager.write_config(configs=configs,
                               config_num=value,
                               config_letter=name)


"""
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
"""
skip = [0.25, 0.5, 0.75]
turbo_prob = [0.01, 0.05, 0.1]
turbo_factor = [5, 10, 20]
disable_prob = [0.1, 0.25, 0.5]
weight_mutate_power = [0.1, 0.25, 0.5]
link_mutate_prob = [0.1, 0.25, 0.5]
node_mutate_prob = [0.1, 0.25, 0.5]
mutate_bias_prob = [0.1, 0.25, 0.5]
new_link_prob = [0.05, 0.1, 0.25]
add_link_prob = [0.05, 0.1, 0.25]
add_node_prob = [0.05, 0.1, 0.25]

for num, val in enumerate(skip, 1):
    create_config(category="NEAT",
                name="skip_connection",
                variation=num,
                value=val)
    
for num, val in enumerate(turbo_prob, 1):
    create_config(category="NEAT",
                name="turbo_prob",
                variation=num,
                value=val)
    
for num, val in enumerate(turbo_factor, 1):
    create_config(category="NEAT",
                name="turbo_factor",
                variation=num,
                value=val)
    
for num, val in enumerate(disable_prob, 1):
    create_config(category="NEAT",
                name="disable_prob",
                variation=num,
                value=val)
    
for num, val in enumerate(weight_mutate_power, 1):
    create_config(category="NEAT",
                name="weight_mutate_power",
                variation=num,
                value=val)
    
    
for num, val in enumerate(link_mutate_prob, 1):
    create_config(category="NEAT",
                name="link_mutate_prob",
                variation=num,
                value=val)
    
    
for num, val in enumerate(node_mutate_prob, 1):
    create_config(category="NEAT",
                name="node_mutate_prob",
                variation=num,
                value=val)
    
for num, val in enumerate(mutate_bias_prob, 1):
    create_config(category="NEAT",
                name="mutate_bias_prob",
                variation=num,
                value=val)
    
for num, val in enumerate(new_link_prob, 1):
    create_config(category="NEAT",
                name="new_link_prob",
                variation=num,
                value=val)
    
for num, val in enumerate(add_link_prob, 1):
    create_config(category="NEAT",
                name="add_link_prob",
                variation=num,
                value=val)
    
for num, val in enumerate(add_node_prob, 1):
    create_config(category="NEAT",
                name="add_node_prob",
                variation=num,
                value=val)

"""
"animal_sparsity": 5
# Entity
"initial_size": 20,
"init_action_cost": 1,
"max_age_size_coeff": 5,
"growth_energy_required": 10,
"child_energy_cost_divisor": 2,
#Animal
"init_adult_size": 5,
"init_blue_energy": 100,
"init_red_energy": 100,
"reproduction_cost": 10,
"planting_cost": 10,
#Tree
"init_blue_energy": 100,
"init_red_energy": 100, """

""" animal_sparsity = [1, 2, 3, 4, 5]

initial_size = [5, 10, 20, 50, 100]
initial_action_cost = [0, 1, 2, 3, 4, 5]
max_age_size_coeff = [1, 5, 10, 100]
growth_energy_required = [1, 5, 10, 100]
child_energy_cost_divisor = [1, 2, 5, 10]

init_adult_size = [1, 5, 10, 100]
init_blue_energy = [100, 1000, 10000, 100000]
init_red_energy = [100, 1000, 10000, 100000]
reproduction_cost = [1, 2, 3]
planting_cost = [1, 5, 10]

for num,val in enumerate(animal_sparsity, 1):
    create_config(category="Simulation",
                name="animal_sparsity",
                variation=num,
                value=val)
    
for num,val in enumerate(initial_size, 1):
    create_config(category="Simulation",
                  subcategory="Entity",
                name="initial_size",
                variation=num,
                value=val)

for num,val in enumerate(initial_action_cost, 1):
    create_config(category="Simulation",
                  subcategory="Entity",
                name="initial_action_cost",
                variation=num,
                value=val)

for num,val in enumerate(max_age_size_coeff, 1):
    create_config(category="Simulation",
                  subcategory="Entity",
                    name="max_age_size_coeff",
                    variation=num,
                    value=val)
    
for num,val in enumerate(growth_energy_required, 1):
    create_config(category="Simulation",
                  subcategory="Entity",
                name="growth_energy_required",
                variation=num,
                value=val)
    
for num,val in enumerate(child_energy_cost_divisor, 1):
    create_config(category="Simulation",
                  subcategory="Entity",
                name="child_energy_cost_divisor",
                variation=num,
                value=val)
    
for num,val in enumerate(init_adult_size, 1):
    create_config(category="Simulation",
                  subcategory="Animal",
                name="init_adult_size",
                variation=num,
                value=val)
    
for num,val in enumerate(init_blue_energy, 1):
    create_config(category="Simulation",
                  subcategory="Animal",
                name="init_blue_energy",
                variation=num,
                value=val)
    
for num,val in enumerate(init_red_energy, 1):
    create_config(category="Simulation",
                subcategory="Animal",
                name="init_red_energy",
                variation=num,
                value=val)
    
for num,val in enumerate(reproduction_cost, 1):
    create_config(category="Simulation",
                  subcategory="Animal",
                name="reproduction_cost",
                variation=num,
                value=val)
    
for num,val in enumerate(planting_cost, 1):
    create_config(category="Simulation",
                  subcategory="Animal",
                name="planting_cost",
                variation=num,
                value=val) """
