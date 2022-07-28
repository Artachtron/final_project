from msilib import init_database

from numpy import gradient
from pygame import init

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
init_blue_energy = [10, 100, 1000, 10000]
init_red_energy = [10, 100, 1000, 10000]
reproduction_cost = [1, 5, 10]
planting_cost = [1, 5, 10]

