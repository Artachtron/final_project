
from __future__ import annotations

from simulation import Simulation, SimState
from environment import Environment
from display import Display

import numpy as np
from typing import Tuple, Final


grid = None

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
        self.environment: Environment
        self.display: Display
        
        self._init_world()
    
    @property
    def id(self):
        return self.__id
        
    def _init_world(self):   
        self.environment = Environment(env_id=self.id)
                   
        self.simulation = Simulation(sim_id=self.id,
                                     environment=self.environment)
        
        self.display = Display(display_id=self.id,
                              dimensions=self.dimensions,
                              block_size=self.block_size)
        
    
            
        
    def update(self):
        self.grid.update()
        self.simulation.update()
        
        if self.display_active:
            self.diplay.update()   
   
             
""" def main():
    configure()

    init_world()
      
    while True:
        #update_world()
        display.main() """        

""" def configure():
    internal_properties = 4
    see_entities = 8
    see_energies = 9
    see_cells = 25 * 3
    n_inputs = internal_properties + see_entities + see_energies + see_cells
    
    move = 2
    modify_cell_color = 3
    drop_energy = 2
    other_actions = 5
    n_outputs = move + modify_cell_color + drop_energy + other_actions
    
    Config.configure(num_inputs=n_inputs,
                              num_outputs=n_outputs)
    Config.num_inputs = n_inputs
    Config.num_outputs = n_outputs 
    print(Config.num_inputs, Config.num_outputs) """
            

    
    

       
def get_random_coordinates() -> Tuple[int,int]:
    """Get random coordinates of a point on a grid

    Returns:
        Tuple[int,int]: coordinates generated randomly
    """      
    return np.random.randint(0, grid.dimensions[0]), np.random.randint(0,grid.dimensions[1])
    
def init_trees(count: int=0) -> None:
    """Initialize the population of trees

    Args:
        count (int, optional): number of trees to create. Defaults to 0.
    """    
    
    for _ in range(count):
        create_new_tree()
        
def create_new_tree():
    """Create a new tree in a vacant cell
    """    
    x, y = get_random_coordinates()
    
    while grid.entity_grid.get_cell_value(cell_coordinates=(x,y)):
       x, y = get_random_coordinates()
    
    grid.create_entity(entity_type="tree", position=(x,y), blue_energy=20, max_age=10)
    
def init_energies() -> None:
    """Initialize the energies on the grid (only for tests)
    """
    pass
        
def main():
    pass
           
if __name__ == "__main__":
    main()
    

