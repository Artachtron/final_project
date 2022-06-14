from typing import Tuple

class Position:
    def __init__(self,
                 position: Tuple[int, int]):
        
        self._x = position[0]
        self._y = position[1]
        
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
        

class SimulatedObject:
    def __init__(self,
                 sim_body_id: int,
                 position: Tuple[int, int]):
    
        self.id = sim_body_id
        self.position = Position(position=position)
        
class Simulation:
    def __init__(self,
                 sim_id: int):
    
        self.id = sim_id
        

