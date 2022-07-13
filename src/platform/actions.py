
from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple

from energies import EnergyType
from entities import Status


class ActionType(Enum):
    """Enum:
        Type of action
    """
    MOVE = auto()
    PAINT = auto()
    DROP = auto()
    PICKUP = auto()
    RECYCLE = auto()
    PLANT_TREE = auto()
    GROW = auto()
    REPRODUCE = auto()

@dataclass
class Action(ABC):
    """Abstract class:
        Contains necessary information for an action
    """
    action_type: ActionType

@dataclass
class SelfAction(Action):
    """Superclass:
        Actions that do not modify the environment
    """
    new_status: Optional[Status]


@dataclass
class Interaction(Action):
    """Superclass:
        Actions that modify the environment
    """
    coordinates: Tuple[int, int]

@dataclass
class ReproduceAction(SelfAction):
    """SelfAction:
        Action on decision to reproduce
    """
    new_status = Status.FERTILE
    action_type = ActionType.REPRODUCE

@dataclass
class GrowAction(SelfAction):
    """SelfAction:
        Action on decision to grow
    """
    action_type = ActionType.GROW

@dataclass
class PlantTree(Interaction):
    """Interaction:
        Action on decision to plant a tree
    """
    action_type = ActionType.PLANT_TREE

@dataclass
class RecycleAction(Interaction):
    """Interaction:
        Action on decision to recycle a seed
    """
    action_type = ActionType.RECYCLE

@dataclass
class PickupAction(Interaction):
    """Interaction:
        Action on decision to pick up resource
    """
    action_type = ActionType.PICKUP

@dataclass
class DropAction(Interaction):
    """Interaction:
        Action on decision to drop resource
    """
    action_type = ActionType.DROP
    energy_type: EnergyType
    quantity: int

@dataclass
class PaintAction(Interaction):
    """Interaction:
        Action on decision to modify a cell's color
    """
    action_type = ActionType.PAINT
    color: Tuple[int, int, int]

@dataclass
class MoveAction(Interaction):
    """Interaction:
        Action on decision to move
    """
    action_type = ActionType.MOVE

