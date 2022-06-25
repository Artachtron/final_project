from __future__ import annotations
    
from typing import Tuple, Optional

import enum
from numpy.random import randint
from math import log

from universal import SimulatedObject


class Resource(SimulatedObject):
    def __init__(self,
                 resource_id: int,
                 position: Tuple[int, int],
                 size: int = 10,
                 appearance: str = "",
                 quantity: int = None
                 ):
        
        self.quantity = quantity or randint(10,100)
        print(quantity)
        size: int = 5 + log(quantity, 2)
        # size = size/50 if size > 50 else size
        
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
                 owner_id: Optional[int] = 0,
                 ):
        
        appearance = "energies/" + appearance
        super(Energy, self).__init__(resource_id=energy_id,
                                     position=position,
                                     size=10,
                                     appearance=appearance,
                                     quantity=quantity)
        
        self._type: EnergyType = energy_type
        self.owner = owner_id
        
    @property
    def type(self):
        return self._type

class RedEnergy(Energy):
    def __init__(self,
                 position: Tuple[int,int],
                 energy_id: int = 0,
                 quantity: int = 10,
                 owner_id: Optional[int] = 0,
                 ):
        
        super(RedEnergy, self).__init__(energy_id=energy_id,
                                        position=position,
                                        quantity=quantity,
                                        appearance="red_energy.png",
                                        energy_type=EnergyType.RED,
                                        owner_id=owner_id)
        
class BlueEnergy(Energy):
    def __init__(self,
                 position: Tuple[int,int],
                 energy_id: int = 0,
                 quantity: int = 10,
                 owner_id: Optional[int] = 0,
                 ):
        
        super(BlueEnergy, self).__init__(energy_id=energy_id,
                                         position=position,
                                         quantity=quantity,
                                         appearance="blue_energy.png",
                                         energy_type=EnergyType.BLUE,
                                         owner_id=owner_id)