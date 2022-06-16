from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from grid import Grid
    from environment import Environment
    
from typing import Tuple

import enum
from numpy.random import randint

from simulation import SimulatedObject


class Resource(SimulatedObject):
    def __init__(self,
                 resource_id: int,
                 environment: Environment,
                 position: Tuple[int, int],
                 size: int = 10,
                 appearance: str = "",
                 quantity: int = 0
                 ):
        
        self.quantity = quantity or randint(10,100)
        size: int = max(10, quantity)
        
        appearance = "models/resources/" + appearance
        super(Resource, self).__init__(sim_obj_id=resource_id,
                                       environment=environment,
                                       position=position,
                                       size=size,
                                       appearance=appearance)
        
         
class EnergyType(enum.Enum):
    BLUE = "blue energy"
    RED = "red energy"

class Energy(Resource):
    def __init__(self,
                 energy_id: int,
                 environment: Environment,
                 energy_type: EnergyType,
                 position: Tuple[int,int],
                 quantity: int = 10,
                 appearance: str = "",
                 ):
        
        appearance = "energies/" + appearance
        super(Energy, self).__init__(resource_id=energy_id,
                                     environment=environment,
                                     position=position,
                                     size=10,
                                     appearance=appearance,
                                     quantity=quantity)
        
        self._type: EnergyType = energy_type
        
    @property
    def type(self):
        return self._type
    
    @staticmethod
    def generate(energy_type: EnergyType, position: Tuple[int, int],
                 quantity: int, grid: Grid = None) -> Energy:
        
        match energy_type.value:
            case EnergyType.BLUE.value:
                energy = BlueEnergy(position=position,
                                    quantity=quantity)
                
            case EnergyType.RED.value:
                energy = RedEnergy(position=position,
                                   quantity=quantity)
        if grid:       
            grid.place_resource(value=energy)
                
        return energy

class RedEnergy(Energy):
    def __init__(self,
                 position: Tuple[int,int],
                 environment: Environment = None,
                 energy_id: int = 0,
                 quantity: int = 10,
                 ):
        
        super(RedEnergy, self).__init__(energy_id=energy_id,
                                        environment=environment,
                                        position=position,
                                        quantity=quantity,
                                        appearance="red_energy.png",
                                        energy_type=EnergyType.RED)
        
class BlueEnergy(Energy):
    def __init__(self,
                 position: Tuple[int,int],
                 environment: Environment = None,
                 energy_id: int = 0,
                 quantity: int = 10):
        
        super(BlueEnergy, self).__init__(energy_id=energy_id,
                                         environment=environment,
                                         position=position,
                                         quantity=quantity,
                                         appearance="blue_energy.png",
                                         energy_type=EnergyType.BLUE)