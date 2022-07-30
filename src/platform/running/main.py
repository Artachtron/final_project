import cProfile
import pstats

from ..world import World
from .config import config

# py-spy record -o profile.svg --subprocesses -- python -m src.platform.main
# python -m cProfile -m src.platform.main
# python -m src.platform.main
# python -m src.platform.running.main --c config_A_5.json
# snakeviz ./profile.prof


def main():

    world = World(world_id=0,
                #   dimensions=(config['Simulation']['grid_width'],
                #               config['Simulation']['grid_height']),
                #   block_size=config['Simulation']['block_size'],
                #   sim_speed=config['Simulation']['simulation_speed'],
                display_active=False)

    world.init(show_grid=True)
    world.run()

    metrics = world.metrics
    print(metrics.total_animals, metrics.max_generation)

def profile(profiler):
    stats = pstats.Stats(profiler)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats(filename='profile.prof')

if __name__ == '__main__':
    with cProfile.Profile() as pr:
        main()

    profile(profiler=pr)

