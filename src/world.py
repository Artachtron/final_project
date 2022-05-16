import pygame as pg
import sys
from grid import Grid

import numpy as np
from typing import Tuple, Final

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

GRID_HEIGHT: Final[int] = 20
GRID_WIDTH: Final[int] = 20
BLOCK_SIZE: Final[int] = 20

SIMULATION_SPEED: Final[int] = 20

WINDOW_HEIGHT: Final[int] = BLOCK_SIZE * GRID_HEIGHT
WINDOW_WIDTH: Final[int] = BLOCK_SIZE * GRID_WIDTH

INITIAL_ANIMAL_POPULATION: Final[int] = 10
INITIAL_TREE_POPULATION: Final[int] = 2

             
def main():
    global tick_counter
    tick_counter = 0
    
    init_pygame()
    init_world()
      
    while True:
        update_world()
        draw_world()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        pg.display.update()
        CLOCK.tick(60)
        tick_counter += 1
        if tick_counter == SIMULATION_SPEED:
            tick_counter = 0
def init_grid():
    global grid
    grid = Grid(height=GRID_HEIGHT, width=GRID_WIDTH, block_size=BLOCK_SIZE)

 
def init_world() -> None:
    """Initialize the world
    """    
    init_grid()
    init_population(counts=(INITIAL_ANIMAL_POPULATION, INITIAL_TREE_POPULATION))
    init_energies()
 
def init_pygame() -> None:
    """Initialize pygame"""
    global SCREEN, CLOCK
    pg.init()
    SCREEN = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pg.time.Clock()
   
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
    
    grid.create_entity(entity_type="animal", position=(x,y), blue_energy=100)
       
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
    
    grid.create_entity(entity_type="tree", position=(x,y))
    
def init_energies() -> None:
    """Initialize the energies on the grid (only for tests)
    """
    pass
           
def draw_world() -> None:
    """Draw the world, grid and entities"""
    draw_grid()
    draw_entities()
    draw_energies()
    
def draw_grid() -> None:
    """Draw the grid"""
    #SCREEN.fill(WHITE)
    color_grid = grid.color_grid.subgrid
    for x in range(0, WINDOW_WIDTH, BLOCK_SIZE):
        for y in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
            rect = pg.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pg.draw.rect(SCREEN, color_grid[int(x/BLOCK_SIZE),int(y/BLOCK_SIZE)], rect, 0)
            pg.draw.rect(SCREEN, BLACK, rect, 1)

def update_world() -> None:
    """Update the world"""
    if tick_counter == 0:
        update_entities()

    #print(grid.grid.transpose())

def update_entities() -> None:
    """Update the entities"""
    grid.entity_group.update()
        
def draw_entities() -> None:
    """Draw the entities"""
    grid.entity_group.draw(SCREEN)

def draw_energies() -> None:
    """Draw the energies"""
    grid.energy_group.draw(SCREEN)
  
if __name__ == "__main__":
    main()