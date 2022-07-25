import os
import sys

from project.src.platform.actions import *
from project.src.platform.energies import EnergyType
from project.src.platform.entities import Status


class TestActions:
    def test_self_actions(self):
        # ReproduceAction
        reproduce_action = ReproduceAction(new_status=Status.FERTILE)
        
        assert reproduce_action.new_status == Status.FERTILE
        assert reproduce_action.action_type == ActionType.REPRODUCE
        
        # GrowAction
        grow_action = GrowAction()
        
        assert grow_action.new_status == None
        assert grow_action.action_type == ActionType.GROW
        
        
    def test_interactions(self):
        # plant tree
        plant_action = PlantTreeAction(coordinates=(2,3),
                                       seed=None)

        assert plant_action.coordinates == (2,3)
        assert plant_action.action_type == ActionType.PLANT_TREE
        
        # recycle seed
        recycle_action = RecycleAction(coordinates=(2,3),
                                       tree=None)
        assert recycle_action.coordinates == (2,3)
        assert recycle_action.action_type == ActionType.RECYCLE
        
        # pickup resource
        pickup_action = PickupAction(coordinates=(2,3))
        assert pickup_action.coordinates == (2,3)
        assert pickup_action.action_type == ActionType.PICKUP
        
        # drop resource
        drop_action = DropAction(coordinates=(2,3),
                                 quantity=10,
                                 energy_type=EnergyType.BLUE)
        
        assert drop_action.action_type == ActionType.DROP
        assert drop_action.coordinates == (2,3)
        assert drop_action.quantity == 10
        assert drop_action.energy_type == EnergyType.BLUE
        
        # paint cell
        paint_action = PaintAction(coordinates=(2,3),
                                   color=(10,12,15))
        
        assert paint_action.action_type == ActionType.PAINT
        assert paint_action.coordinates == (2,3)
        assert paint_action.color == (10,12,15)
        
        # move
        move_action = MoveAction(coordinates=(2,3))
        
        assert move_action.action_type == ActionType.MOVE
        assert move_action.coordinates == (2,3)
