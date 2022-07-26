import cProfile
import pstats

from .config import ConfigManager, config
from .world import World

# py-spy record -o profile.svg --subprocesses -- python -m src.platform.main
# python -m src.platform.main  
# python -m cProfile -m src.platform.main

def main():

    #write_config()

    world = World(world_id=0,
                  dimensions=(config['Simulation']['grid_width'],
                              config['Simulation']['grid_height']),
                  block_size=config['Simulation']['block_size'],
                  sim_speed=config['Simulation']['simulation_speed'],
                  display_active=False)

    world.init(show_grid=True)
    world.run()

def write_config():
    d = {
            "NEAT":{
                    # Mutations
                    ## Link mutation
                    "disable_prob": 10,
                    "enable_prob": 12,
                    "weight_mutate_power": 13,
                    "link_mutate_prob": 15
            }
        }
    ConfigManager.write_config(configs=d,
                               config_num=1)



if __name__ == '__main__':
    with cProfile.Profile() as pr:
        main()
        
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats(filename='profile.prof')
