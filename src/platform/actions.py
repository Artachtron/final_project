from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from energies import EnergyType
    from entities import Seed, Tree

from abc import ABC
from dataclasses import dataclass
from enum import Enum, auto


class Status(Enum):
    """Enum:
        Entity status
    """
    ALIVE = 0
    DEAD = 1
    FERTILE = 2

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
    PRODUCE_ENERGY = auto()
    IDLE = auto()

@dataclass(kw_only=True, frozen=True)
class Action(ABC):
    """Abstract class:
        Contains necessary information for an action
    """
    action_type: ActionType

@dataclass(kw_only=True, frozen=True)
class SelfAction(Action):
    """Superclass:
        Actions that do not modify the environment
    """
    new_status: Optional[Status] = None

@dataclass(kw_only=True, frozen=True)
class Interaction(Action):
    """Superclass:
        Actions that modify the environment
    """
    coordinates: Tuple[int, int]

@dataclass(kw_only=True, frozen=True)
class ReproduceAction(SelfAction):
    """SelfAction:
        Action on decision to reproduce
    """
    action_type: ActionType = ActionType.REPRODUCE
    new_status: Status = Status.FERTILE

@dataclass(kw_only=True, frozen=True)
class GrowAction(SelfAction):
    """SelfAction:
        Action on decision to grow
    """
    action_type: ActionType = ActionType.GROW
    
@dataclass(kw_only=True, frozen=True)
class ProduceEnergyAction(Interaction):
    """SelfAction:
        Action on decision to produce energy
    """
    action_type: ActionType = ActionType.PRODUCE_ENERGY
    energy_type: EnergyType
    
@dataclass(kw_only=True, frozen=True)
class IdleAction(SelfAction):
    """SelfAction:
        Action to do nothing
    """
    action_type: ActionType = ActionType.IDLE

@dataclass(kw_only=True, frozen=True)
class PlantTreeAction(Interaction):
    """Interaction:
        Action on decision to plant a tree
    """
    action_type: ActionType = ActionType.PLANT_TREE
    seed: Optional[Seed]

@dataclass(kw_only=True, frozen=True)
class RecycleAction(Interaction):
    """Interaction:
        Action on decision to recycle a seed
    """
    action_type: ActionType = ActionType.RECYCLE
    tree: Tree

@dataclass(kw_only=True, frozen=True)
class PickupAction(Interaction):
    """Interaction:
        Action on decision to pick up resource
    """
    action_type: ActionType = ActionType.PICKUP

@dataclass(kw_only=True, frozen=True)
class DropAction(Interaction):
    """Interaction:
        Action on decision to drop resource
    """
    action_type: ActionType = ActionType.DROP
    energy_type: EnergyType
    quantity: int

@dataclass(kw_only=True, frozen=True)
class PaintAction(Interaction):
    """Interaction:
        Action on decision to modify a cell's color
    """
    action_type: ActionType = ActionType.PAINT
    color: Tuple[int, int, int]

@dataclass(kw_only=True, frozen=True)
class MoveAction(Interaction):
    """Interaction:
        Action on decision to move
    """
    action_type: ActionType = ActionType.MOVE
