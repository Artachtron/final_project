from .config import ConfigManager, config
from .world import World


def main():

    #write_config()

    world = World(world_id=0,
                  dimensions=(config['Simulation']['grid_width'],
                              config['Simulation']['grid_height']),
                  block_size=config['Simulation']['block_size'],
                  sim_speed=config['Simulation']['simulation_speed'],
                  display_active=True)

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
    main()
