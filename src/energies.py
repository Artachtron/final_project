import enum
from os.path import dirname, realpath, join
from pathlib import Path
import pygame as pg

from typing import Tuple

assets_path = join(Path(dirname(realpath(__file__))).parent.absolute(), "assets/models/energies")

class EnergyType(enum.Enum):
    BLUE = 0
    RED = 1

class Energy(pg.sprite.Sprite):
    def __init__(self,
                 energy_type: EnergyType,
                 image_filename: str,
                 grid,
                 position: Tuple[int,int],
                 quantity: int = 10,
                 ):
        super().__init__()
        self.type = energy_type
        self.quantity = quantity
        size = 10
        self.position = position
        
        image = pg.image.load(join(assets_path, image_filename)).convert_alpha()
        self.image = pg.transform.scale(image, (size,size))
        pos_x, pos_y = self.position
        self.rect = self.image.get_rect(center=(pos_x *grid.BLOCK_SIZE +grid.BLOCK_SIZE/2, pos_y * grid.BLOCK_SIZE + grid.BLOCK_SIZE/2))
        
        self.grid = grid
        self.grid.update_grid_cell_value(position=(self.position), value=1)

class RedEnergy(Energy):
    def __init__(self, *args, **kwargs):
        super(RedEnergy, self).__init__(image_filename="red_energy.png", energy_type=EnergyType.RED ,*args, **kwargs)
        
class BlueEnergy(Energy):
    def __init__(self, *args, **kwargs):
        super(BlueEnergy, self).__init__(image_filename="blue_energy.png", energy_type=EnergyType.BLUE ,*args, **kwargs)