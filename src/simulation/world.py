
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
    BLOCK_SIZE: Final[int] = 50
    MAX_CYCLE = 1000

    SIMULATION_SPEED: Final[int] = 20 
    
    def __init__(self,
                 world_id: int,
                 dimensions: Tuple[int, int] = (GRID_HEIGHT,
                                                GRID_WIDTH),
                 block_size: int = BLOCK_SIZE,
                 sim_speed: int = SIMULATION_SPEED,
                 display_active: bool = False):
        
        self.__id: int = world_id
        self.dimensions: Tuple[int, int] = dimensions
        self.block_size: int = block_size
        self.sim_speed: int = sim_speed
        self.display_active: bool = display_active
        self.running: bool = False
    
        self.simulation: Simulation
        self.display: Display
        
            
    @property
    def id(self):
        return self.__id
        
    def init(self):   
        self.simulation = Simulation(sim_id=self.id,
                                     dimensions=self.dimensions)
           
        sim_state = self.simulation.init()
        
        if self.display_active:
            self.display = Display(display_id=self.id,
                                dimensions=self.dimensions,
                                block_size=self.block_size,
                                sim_speed=self.sim_speed)
        
            self.display.init(sim_state=sim_state)
        
     
    def populate(self):
        self.simulation.populate()   
      
    def update(self):
        grid, sim_state = self.simulation.update()
        
        if self.display_active:
            self.display.update(sim_state=sim_state)
            self.display.draw(grid)  
        
        if sim_state.cycle == World.MAX_CYCLE:
            print("SHUTDOWN")
            self.shutdown()
            
    def shutdown(self):
        self.running = False         
             
    def run(self):
        self.running = True       
        while self.running:
            self.update()
                   
          


    

