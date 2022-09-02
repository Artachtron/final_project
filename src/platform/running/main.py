import cProfile
import pstats
from cProfile import Profile
from time import time

from ..world import World
from .config import config

# py-spy record -o profile.svg --subprocesses -- python -m src.platform.main
# python -m cProfile -m src.platform.main
# python -m src.platform.main
# python -m src.platform.running.main --c config_A_5.json
# snakeviz ./profile.prof


def main():
    start = time()
    world = World(world_id=0,
                  display_active=config.display,
                  probe=True)

    world.init(show_grid=True)
    
    try:
        world.run()
    except Exception as e:
        print(f"exception: {repr(e)}")
    end = time()
    print(f'It took {(end - start)/60: .0f} minutes!')
    world.write_metrics()
    """ world.save_simulation()
    world.write_metrics()
    world.graph_metrics() """

def profile(profiler: Profile):
    """Function:
        Save execution timing stats
        of the simulation's run
        into a profile file

    Args:
        profiler (Profile): Keep track of execution timing for all calls
    """
    stats = pstats.Stats(profiler)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.get_stats_profile()
    stats.dump_stats(filename='profile.prof')



if __name__ == '__main__':
    with cProfile.Profile() as pr:
        main()

    profile(profiler=pr)
