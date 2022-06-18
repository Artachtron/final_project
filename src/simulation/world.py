
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from grid import Grid

from simulation import Simulation
from display import Display

from typing import Tuple, Final


INITIAL_ANIMAL_POPULATION: Final[int] = 10
INITIAL_TREE_POPULATION: Final[int] = 2

        
class World:
    GRID_HEIGHT: Final[int] = 20
    GRID_WIDTH: Final[int] = 20
    BLOCK_SIZE: Final[int] = 20

    SIMULATION_SPEED: Final[int] = 20 
    
    def __init__(self,
                 world_id: int,
                 dimensions: Tuple[int, int] = (GRID_HEIGHT,
                                                GRID_WIDTH),
                 block_size: int= BLOCK_SIZE,
                 sim_speed: int = SIMULATION_SPEED,
                 display_active: bool = False):
        
        self.__id: int = world_id
        self.dimensions: Tuple[int, int] = dimensions
        self.block_size: int = block_size
        self.sim_speed: int = sim_speed
        self.display_active: bool = display_active
    
        self.simulation: Simulation
        self.display: Display
            
    @property
    def id(self):
        return self.__id
        
    def init(self):   
        self.simulation = Simulation(sim_id=self.id,
                                     dimensions=self.dimensions)
        
        self.display = Display(display_id=self.id,
                              dimensions=self.dimensions,
                              block_size=self.block_size,
                              sim_speed=self.sim_speed)
        
        
        sim_state = self.simulation.init(display=self.display_active)
        self.display.init(sim_state=sim_state)
        
    
            
        
    def update(self):
        grid = self.simulation.update()
        
        if self.display_active:
            self.display.update()
            self.display.draw(grid)   
   
             
    def run(self):
        #configure()        
        while True:
            self.update()
                   
          


    

