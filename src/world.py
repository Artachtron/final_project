import display
from grid import Grid

import numpy as np
from typing import Tuple, Final


INITIAL_ANIMAL_POPULATION: Final[int] = 10
INITIAL_TREE_POPULATION: Final[int] = 2

             
def main():
    configure()
    
    display.init_pygame()
    init_world()
      
    while True:
        update_world()
        display.main()        

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
            
def init_grid():
    global grid
    grid = Grid(height=GRID_HEIGHT, width=GRID_WIDTH, block_size=BLOCK_SIZE)

def init_world() -> None:
    """Initialize the world
    """    
    init_grid()
    init_population(counts=(INITIAL_ANIMAL_POPULATION, INITIAL_TREE_POPULATION))
    init_energies()
   
def init_population(**kwargs) -> None:
    """Populate the world with the initial population
    """    
    animals_count, trees_count = kwargs['counts']
  
    init_animals(count=animals_count)
    init_trees(count=trees_count)
    
def init_animals(count: int = 0) -> None:
    """Initialize the population of animals

    Args:
        count (int, optional): number of animals to create. Defaults to 0.
    """    
    
    for _ in range(count):
        create_new_animal()
    
def create_new_animal() -> None:
    """Create a new animal in a vacant cell
    """
    x, y = get_random_coordinates()
    
    while grid.entity_grid.get_cell_value(cell_coordinates=(x,y)):
        x, y = get_random_coordinates()
    
    animal = grid.create_entity(entity_type="animal", position=(x,y), blue_energy=100)
    
       
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
                   
if __name__ == "__main__":
    main()
    

