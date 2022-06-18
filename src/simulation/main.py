from world import World


GRID_WIDTH = 20
GRID_HEIGHT = 20
BLOCK_SIZE = 20

SIMUMLATION_SPEED = 2

def main():
    world = World(world_id=0,
                      dimensions=(GRID_WIDTH
                                  ,GRID_HEIGHT),
                      block_size= BLOCK_SIZE,
                      sim_speed=SIMUMLATION_SPEED,
                      display_active=True)
            
    world.init()
    world.run()


if __name__ == '__main__':
    main()