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


for num,val in enumerate(animal_sparsity, 1):
    configs={
        "Run": {
            "parameter": "animal_sparsity",
            "variation": num,
        },"Simulation":{
            "animal_sparsity":val
        }
    }
    
    ConfigManager.write_config(configs=configs,
                                config_num=num,
                                config_letter='A')

for num,val in enumerate( initial_size, 1):
    configs={
        "Run": {
"parameter": "initial_size",
        "variation": num,
        },"Simulation":{
            "Entity":
            {
                "initial_size":val
            }
        }
    }
    
    ConfigManager.write_config(configs=configs,
                                config_num=num,
                                config_letter='B')

for num,val in enumerate( initial_action_cost, 1):
    configs={
        "Run": {
"parameter": "initial_action_cost",
        "variation": num,
        },"Simulation":{
            "Entity":
            {
                "initial_action_cost":val
            }
        }
    }
    
    ConfigManager.write_config(configs=configs,
                                config_num=num,
                                config_letter='C')


for num,val in enumerate( max_age_size_coeff, 1):
    configs={
        "Run": {
"parameter": "max_age_size_coeff",
        "variation": num,
        },"Simulation":{
            "Entity":
            {
                "max_age_size_coeff":val
            }
        }
    }
    
    ConfigManager.write_config(configs=configs,
                                config_num=num,
                                config_letter='D')

for num,val in enumerate( growth_energy_required, 1):
    configs={
        "Run": {
"parameter": "growth_energy_required",
        "variation": num,
        },"Simulation":{
            "Entity":
            {
                "growth_energy_required":val
            }
        }
    }
    
    ConfigManager.write_config(configs=configs,
                                config_num=num,
                                config_letter='E')

for num,val in enumerate( child_energy_cost_divisor, 1):
    configs={
        "Run": {
"parameter": "child_energy_cost_divisor",
        "variation": num,
        },"Simulation":{
            "Entity":
            {
                "child_energy_cost_divisor":val
            }
        }
    }
    
    ConfigManager.write_config(configs=configs,
                                config_num=num,
                                config_letter='F')

for num,val in enumerate( init_adult_size, 1):
    configs={
        "Run": {
"parameter": "init_adult_size",
        "variation": num,
        },"Simulation":{
            "Animal":
            {
                "init_adult_size":val
            }
        }
    }
    
    ConfigManager.write_config(configs=configs,
                                config_num=num,
                                config_letter='G')

for num, val in enumerate( init_blue_energy, 1):
    configs={
        "Run": {
"parameter": "animal_init_blue_energy",
        "variation": num,
        },"Simulation":{
            "Animal":
            {
                "init_blue_energy":val
            }
        }
    }
    
    ConfigManager.write_config(configs=configs,
                                config_num=num,
                                config_letter='H')

for num,val in enumerate( init_red_energy, 1):
    configs={
        "Run": {
"parameter": "animal_init_red_energy",
        "variation": num,
        },"Simulation":{
            "Animal":
            {
                "init_red_energy":val
            }
        }
    }
    
    ConfigManager.write_config(configs=configs,
                                config_num=num,
                                config_letter='I')

for num,val in enumerate( reproduction_cost, 1):
    configs={
        "Run": {
"parameter": "reproduction_cost",
        "variation": num,
        },"Simulation":{
            "Animal":
            {
                "reproduction_cost":val
            }
        }
    }
    
    ConfigManager.write_config(configs=configs,
                                config_num=num,
                                config_letter='J')

for num,val in enumerate( planting_cost, 1):
    configs={
        "Run": {
"parameter": "planting_cost",
        "variation": num,
        },"Simulation":{
            "Animal":
            {
                "planting_cost":val
            }
        }
    }
    
    ConfigManager.write_config(configs=configs,
                                config_num=num,
                                config_letter='K')

for num,val in enumerate( init_blue_energy, 1):
    configs={
        "Run": {
"parameter": "tree_init_blue_energy",
        "variation": num,
        },"Simulation":{
            "Tree":
            {
                "init_blue_energy":val
            }
        }
    }
    
    ConfigManager.write_config(configs=configs,
                                config_num=num,
                                config_letter='L')

for num,val in enumerate( init_red_energy, 1):
    configs={
        "Run": {
"parameter": "tree_init_red_energy",
        "variation": num,
        },"Simulation":{
            "Tree":
            {
                "init_red_energy":val
            }
        }
    }
    
    ConfigManager.write_config(configs=configs,
                                config_num=num,
                                config_letter='M')



