from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from display import DisplayedObject
    from grid import Grid
    from entities import Animal, Tree, Entity 
    from environment import Environment
 

from typing import Tuple, Any, Dict   

from dataclasses import dataclass
from math import sqrt

@dataclass
class Position:
    x: int
    y: int
     
    def __call__(self):
        return self.x, self.y
           
    @property
    def vect(self):
        return self.x, self.y
        
    def add(self, vect: Tuple[int, int]):
        self._x += vect[0]
        self._y += vect[1]
     
    @staticmethod   
    def add(position: Position, vect: Tuple[int, int]):
        pos = tuple(position)

        return Position(pos[0] + vect[0], 
                        pos[1] + vect[1])
        
    @staticmethod
    def distance(object1: Any, object2: Any) -> float:
        distance = sqrt((object1.position[0] - object2.position[0])**2 +
                        (object1.position[1] - object2.position[1])**2)
        
        return round(distance, 2)

class SimState:
    def __init__(self,
                 sim_id: int):
        
        self.__id: int = sim_id
        self.next_entity_id: int  = 1
        self.next_energy_id: int = 1
        
        self.animals: Dict[int, Animal] = {}
        self.trees: Dict[int, Tree] = {}
        
        self.grid: Grid
        
        self._init_sim_state()
        
    def _init_sim_state(self):
        from grid import Grid
        self.grid = Grid(grid_id=self.id,
                         dimensions=(20,20))
    
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
                

        
        
class Simulation:
    def __init__(self,
                 sim_id: int,
                 environment: Environment):
    
        self.id = sim_id
        
        self.sim_state: SimState
        self.environment: Environment = environment
        
        self._init_simulation()
    
    def _init_simulation(self):
        self.state = SimState(sim_id=self.id)
        """ self.environment = Environment(env_id=self.id,
                                       sim_state=self.state)    """
    
   
        

class SimulatedObject:
    def __init__(self,
                 sim_obj_id: int,
                 size: int,
                 position: Tuple[int, int],
                 environment: Environment,
                 appearance: str):
    
        self.__id = sim_obj_id
        self._size = size
        self._position = Position(*position)
        self._environment = environment   
               
        self._appearance = appearance
        self.dis_obj: DisplayedObject
        
        
        # self._init_displayed_object()
    
    @property
    def id(self):
        return self.__id

    @property
    def size(self):
        return self._size
    
    @size.setter
    def size(self, value):
        self._size = value
    
    @property
    def position(self):
        return self._position()
    
    @position.setter
    def position(self, value):
        self._position = Position(*value)
        
    @property
    def environment(self):
        return self._environment
        
    def _init_displayed_object(self):
        try:
            self.dis_obj = DisplayedObject(dis_obj_id=self.id,
                                        size=self._size,
                                        position=self._position,
                                        appearance=self._appearance)
        except AttributeError:
            pass
        
        except FileNotFoundError:
            pass