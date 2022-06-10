
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from entities import Entity, Animal, Tree
    

class WorldTable:
    next_entity_id: int  = 1

    entities = []
    
    animal_count: int = 0
    tree_count: int = 0
     
    @staticmethod    
    def get_next_entity_id(increment: bool=False) -> int:
        """ Get the current innovation number

        Returns:
            int: current innovation number
        """
        number = WorldTable.next_entity_id
        
        if increment:
            WorldTable.increment_entity_id()
         
        return number
    
    @staticmethod
    def increment_entity_id(amount: int=1) -> None:
        """ Increment the current innovation number by a given amount

        Args:
            number (int, optional): innovation number's increment. Defaults to 1.
        """        
        WorldTable.next_entity_id += amount
        
    
    @staticmethod
    def add_entity(new_entity: Entity) -> None:
        """ Add an innovation to the history's list of innovations

        Args:
            new_innovation (Innovation): innovation to add to the list
        """        
        WorldTable.history.append(new_entity)
        
        match new_entity.__class__.__name__:
            case "Animal":
                WorldTable.animal_count += 1
            case "Tree":
                WorldTable.tree_count +=1
        
    @staticmethod
    def reset_innovation_table() -> None:
        """ Reset the values of the innovation table
        """       
         
        WorldTable.history = []
        WorldTable.next_entity_id = 1
        
