from typing import Optional

from .config import ConfigManager

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

animal_sparsity = [1, 2, 3, 4, 5]

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
                value=val)
