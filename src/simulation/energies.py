import enum
from os.path import dirname, realpath, join
from pathlib import Path
import pygame as pg

from typing import Tuple
from simulation import SimulatedObject

assets_path = join(Path(dirname(realpath(__file__))).parent.absolute(), "assets/models/energies")


class Resource(SimulatedObject):
    def __init__(self,
                 resource_id: int,
                 position: Tuple[int, int]):
        
        super(Resource, self).__init__(sim_obj_id=resource_id,
                                       position=position) 
            

class EnergyType(enum.Enum):
    BLUE = "blue energy"
    RED = "red energy"

class Energy(pg.sprite.Sprite):
    def __init__(self,
                 energy_type: EnergyType,
                 image_filename: str,
                 grid,
                 position: Tuple[int,int],
                 quantity: int = 10,
                 ):
        
        super().__init__()
        self.type: EnergyType = energy_type
        self.quantity: int = quantity
        size: int = max(10, quantity)
        self.position: Tuple[int,int] = position
        
        image: pg.Surface = pg.image.load(join(assets_path, image_filename)).convert_alpha()
        self.image: pg.Surface = pg.transform.scale(image, (size,size))
        pos_x, pos_y = self.position
        self.rect: pg.Rect = self.image.get_rect(center=(pos_x *grid.BLOCK_SIZE +grid.BLOCK_SIZE/2, pos_y * grid.BLOCK_SIZE + grid.BLOCK_SIZE/2))
        
        self.resource_grid = grid.resource_grid
        self.resource_grid.set_cell_value(cell_coordinates=(self.position), value=self)

class RedEnergy(Energy):
    def __init__(self, *args, **kwargs):
        super(RedEnergy, self).__init__(image_filename="red_energy.png", energy_type=EnergyType.RED ,*args, **kwargs)
        
class BlueEnergy(Energy):
    def __init__(self, *args, **kwargs):
        super(BlueEnergy, self).__init__(image_filename="blue_energy.png", energy_type=EnergyType.BLUE ,*args, **kwargs)