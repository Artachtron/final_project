import pickle

from ..display import Display
from .config import config

# python -m src.platform.running.play_frames -c new_config.json -l sim_frames

def main():
    frames = pickle.load(open('simulations/frames/' + config.loaded_simulation, "rb"))

    dimensions = (config['Simulation']['grid_width'],
                  config['Simulation']['grid_height'])
                  
    block_size = config['Simulation']['block_size']
    display = Display(display_id=0,
                        dimensions=dimensions,
                        block_size=block_size,
                        sim_speed=7,
                        show_grid=True)

    display.init()
    display.init_from_frames(frames=frames)

if __name__ == '__main__':
    main()
