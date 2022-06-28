from __future__ import annotations

import enum
from dataclasses import dataclass
from math import sqrt
from typing import Any, Tuple


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
        
    def move(self, vect: Tuple[int, int]):
        self.x += vect[0]
        self.y += vect[1]
     
    @staticmethod   
    def add(position: Position, vect: Tuple[int, int]):
        pos = position()

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
        
        
        self.__id = sim_obj_id
        self._size = size
        self._position = Position(*position)
               
        self._appearance = appearance       
    
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
    def pos(self):
        return self._position
    
    @property
    def appearance(self):
        return self._appearance
                
    