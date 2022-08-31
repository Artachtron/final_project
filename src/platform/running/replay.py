import cProfile
import pickle

from ..display import Display
from .config import config
from .main import profile

# python -m src.platform.running.play_frames -c new_config.json -l sim_frames

def main():
    frames = pickle.load(open('simulations/frames/' + config.loaded_simulation, "rb"))

    dimensions = (config['Simulation']['grid_width'],
                  config['Simulation']['grid_height'])
                  
    block_size = config['Simulation']['block_size']
    display = Display(display_id=0,
                        dimensions=dimensions,
                        block_size=block_size,
                        sim_speed=5)

    display.init()
    display.init_from_frames(frames=frames, first_frame=0.9)

if __name__ == '__main__':
    with cProfile.Profile() as pr:
        main()

    profile(profiler=pr)
