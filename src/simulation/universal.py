from __future__ import annotations


from typing import Tuple, Any
from dataclasses import dataclass
from math import sqrt
import enum

class EntityType(enum.Enum):
    Animal  =   "animal"
    Tree    =   "tree"

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

class SimulatedObject:
    def __init__(self,
                 sim_obj_id: int,
                 size: int,
                 position: Tuple[int, int],
                 appearance: str):
        
        from display import DisplayedObject
        self.__id = sim_obj_id
        self._size = size
        self._position = Position(*position)
               
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