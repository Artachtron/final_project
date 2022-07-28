from __future__ import annotations

import enum
from math import log
from typing import Optional, Tuple

from numpy.random import randint

from .universal import SimulatedObject


class Resource(SimulatedObject):
    """Subclass of SimulatedObject:
        Inanimated objects used as resources by entities

    Attributes:
        quantity (int): collectible amount
    """
    def __init__(self,
                 resource_id: int,
                 position: Tuple[int, int],
                 appearance: str = "",
                 quantity: int = 0
                 ):
        """Super constructor:
            Get the necessary information for a resource

        Args:
            resource_id (int):          unique identifier
            position (Tuple[int, int]): coordinates in the world
            appearance (str, optional): path to the image file. Defaults to "".
            quantity (int, optional):   collectible amount. Defaults to 0.
        """

        self.quantity = quantity or randint(10,100) # collectible amount of resources
        size: int = int(5 + log(quantity, 2))
        # size = size/50 if size > 50 else size

        appearance = "models/resources/" + appearance
        super().__init__(sim_obj_id=resource_id,
                         position=position,
                         size=size,
                         appearance=appearance)


class EnergyType(enum.Enum):
    """Enum:
        Type of energy, BLUE or RED
    """
    BLUE = "blue energy"
    RED = "red energy"

class Energy(Resource):
    """Subclass of Resource:
        Super class for energies

    Attributes:
        type (EnergyType):  BLUE or RED
        owner_id (int):     unique identifier of owner
    """
    def __init__(self,
                 energy_id: int,
                 energy_type: EnergyType,
                 position: Tuple[int,int],
                 quantity: int = 10,
                 appearance: str = "",
                 owner_id: Optional[int] = 0,
                 ):
        """Super constructor:
            Get the necessary information for an energy

        Args:
            energy_id (int):                    unique identifier
            energy_type (EnergyType):           BLUE or RED
            position (Tuple[int,int]):          coordinates in the world
            quantity (int, optional):           collectible amount. Defaults to 10.
            appearance (str, optional):         path to image file. Defaults to "".
            owner_id (Optional[int], optional): unique identifier of owner. Defaults to 0.
        """

        appearance = "energies/" + appearance
        super().__init__(resource_id=energy_id,
                         position=position,
                         appearance=appearance,
                         quantity=quantity)

        self._type: EnergyType = energy_type # BLUE or RED
        self.owner: Optional[int] = owner_id # unique identifier of owner

    @property
    def type(self) -> EnergyType:
        """Property:
            Return the type of Energy

        Returns:
            EnergyType: type of Energy
        """
        return self._type

class RedEnergy(Energy):
    """Subclass of Energy:
        Energy for complex actions, used to prosper
    """
    def __init__(self,
                 position: Tuple[int,int],
                 energy_id: int = 0,
                 quantity: int = 10,
                 owner_id: Optional[int] = 0,
                 ):
        """Constructor:
            Create a red energy

        Args:
            position (Tuple[int,int]):          coordinates in the world
            energy_id (int, optional):          unique identifier. Defaults to 0.
            quantity (int, optional):           collectible amount. Defaults to 10.
            owner_id (Optional[int], optional): unique identifier of the owner. Defaults to 0.
        """

        super().__init__(energy_id=energy_id,
                         position=position,
                         quantity=quantity,
                         appearance="red_energy.png",
                         energy_type=EnergyType.RED,
                         owner_id=owner_id)

class BlueEnergy(Energy):
    """Subclass of Energy:
        Energy for simple actions, used to survive
    """
    def __init__(self,
                 position: Tuple[int,int],
                 energy_id: int = 0,
                 quantity: int = 10,
                 owner_id: Optional[int] = 0,
                 ):
        """Constructor:
            Create a blue energy

        Args:
            position (Tuple[int,int]):          coordinates in the world
            energy_id (int, optional):          unique identifier. Defaults to 0.
            quantity (int, optional):           collectible amount. Defaults to 10.
            owner_id (Optional[int], optional): unique identifier of the owner. Defaults to 0.
        """

        super().__init__(energy_id=energy_id,
                         position=position,
                         quantity=quantity,
                         appearance="blue_energy.png",
                         energy_type=EnergyType.BLUE,
                         owner_id=owner_id)
