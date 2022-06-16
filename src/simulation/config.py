
from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from entities import Entity, Animal, Tree
from typing import Dict

class WorldTable:
    def __init__(self,
                 world_id: int):
        
        self.__id: int = world_id
        self.next_entity_id: int  = 1
        self.next_energy_id: int = 1
        
        self.animals: Dict[int, Animal] = {}
        self.trees: Dict[int, Tree] = {}
    
    @property
    def id(self):
        return self.__id
     
    def get_entity_id(self, increment: bool=False) -> int:
        """ Get the current innovation number

        Returns:
            int: current innovation number
        """
        number = self.next_entity_id
        
        if increment:
            self.increment_entity_id()
         
        return number
    
    def increment_entity_id(self, amount: int=1) -> None:
        """ Increment the current innovation number by a given amount

        Args:
            number (int, optional): innovation number's increment. Defaults to 1.
        """        
        self.next_entity_id += amount
        
    def add_entity(self, new_entity: Entity) -> None:
        """ Add an innovation to the history's list of innovations

        Args:
            new_innovation (Innovation): innovation to add to the list
        """        
            
        match new_entity.__class__.__name__:
            case "Animal":
                self.animals[new_entity.id] = new_entity
            case "Tree":
                self.trees[new_entity.id] = new_entity
        
    
    def reset_world_table(self) -> None:
        """ Reset the values of the innovation table
        """       
         
        self.history = []
        self.next_entity_id = 1
        self.next_energy_id = 1