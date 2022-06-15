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
                 position: Tuple[int, int],
                 size: int = 10,
                 appearance: str = "",
                 quantity: int = 0
                 ):
        
        self.quantity = quantity or randint(10,100)
        size: int = max(10, quantity)
        
        appearance = "models/resources/" + appearance
        super(Resource, self).__init__(sim_obj_id=resource_id,
                                       position=position,
                                       size=size,
                                       appearance=appearance)
        
         
class EnergyType(enum.Enum):
    BLUE = "blue energy"
    RED = "red energy"

class Energy(Resource):
    def __init__(self,
                 energy_id: int,
                 energy_type: EnergyType,
                 position: Tuple[int,int],
                 quantity: int = 10,
                 appearance: str = "",
                 ):
        
        appearance = "energies/" + appearance
        super(Energy, self).__init__(resource_id=energy_id,
                                     position=position,
                                     size=10,
                                     appearance=appearance,
                                     quantity=quantity)
        
        self._type: EnergyType = energy_type

class RedEnergy(Energy):
    def __init__(self, *args, **kwargs):
        super(RedEnergy, self).__init__(appearance="red_energy.png",
                                        energy_type=EnergyType.RED ,
                                        *args, **kwargs)
        
class BlueEnergy(Energy):
    def __init__(self, *args, **kwargs):
        super(BlueEnergy, self).__init__(appearance="blue_energy.png",
                                         energy_type=EnergyType.BLUE ,
                                         *args, **kwargs)