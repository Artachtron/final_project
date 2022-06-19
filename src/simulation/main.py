from world import World


GRID_WIDTH = 50
GRID_HEIGHT = 50
BLOCK_SIZE = 17

SIMUMLATION_SPEED = 20

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