from config import ConfigManager, config
from world import World

GRID_WIDTH = 50
GRID_HEIGHT = 50
BLOCK_SIZE = 17

SIMULATION_SPEED = 20

def main():

    #write_config()

    world = World(world_id=0,
                  dimensions=(GRID_WIDTH,
                              GRID_HEIGHT),
                  block_size=BLOCK_SIZE,
                  sim_speed=SIMULATION_SPEED,
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
