from __future__ import annotations
from typing import Tuple
from display import DisplayedObject

class Position:
    def __init__(self,
                 position: Tuple[int, int]):
        
        self._x = position[0]
        self._y = position[1]
        
    @property
    def vect(self):
        return self._x, self._y
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value
        
    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = value
    
    def add(self, vect: Tuple[int, int]):
        self._x += vect[0]
        self._y += vect[1]
     
    @staticmethod   
    def add(position: Position, vect: Tuple[int, int]):
        pos = tuple(position.vect)

        return Position((pos[0] + vect[0], 
                         pos[1] + vect[1]))
        

class SimulatedObject:
    def __init__(self,
                 sim_obj_id: int,
                 size: int,
                 position: Tuple[int, int],
                 appearance: str):
    
        self.id = sim_obj_id
        self.size = size
        self.position = Position(position=position)
        
        self.appearance = appearance
        self.dis_obj: DisplayedObject
        
        # self._init_displayed_object()
        
    def _init_displayed_object(self):
        try:
            self.dis_obj = DisplayedObject(dis_obj_id=self.id,
                                        size=self.size,
                                        position=self.position,
                                        appearance=self.appearance)
        except AttributeError:
            pass
        
        except FileNotFoundError:
            pass
        
class Simulation:
    def __init__(self,
                 sim_id: int):
    
        self.id = sim_id
        

