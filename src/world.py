import pygame as pg
import sys
from entities import Animal, Tree
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
 
def init_world() -> None:
    """Initialize the world"""
    grid: Grid = Grid(height=GRID_HEIGHT, width=GRID_WIDTH, block_size=BLOCK_SIZE)
    
    init_population(grid=grid, counts=(INITIAL_ANIMAL_POPULATION, INITIAL_TREE_POPULATION))
    init_energies(grid=grid)
 
def init_pygame() -> None:
    """Initialize pygame"""
    global SCREEN, CLOCK
    pg.init()
    SCREEN = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pg.time.Clock()
   
def init_population(grid: Grid, **kwargs) -> None:
    """Populate the world with the initial population
    
    Args:
            grid (Grid): The grid on which the population will be initialized
    """    
    animals_count, trees_count = kwargs['counts']
  
    init_animals(grid=grid, count=animals_count)
    init_trees(grid=grid, count=trees_count)
    
def init_animals(grid: Grid, count: int = 0) -> None:
    """Initialize the population of animals

    Args:
        grid (Grid): grid on which the population will be initialized
        count (int, optional): number of animals to create. Defaults to 0.
    """    
    global animal_group
    animal_group = grid.entity_group
    
    for _ in range(count):
        animal: Animal = create_new_animal(grid=grid)
        animal_group.add(animal)
    
def create_new_animal(grid: Grid) -> Animal:
    """Create a new animal in a vacant cell

    Args:
        grid (Grid): grid on which the animal will be created

    Returns:
        Animal: the newly created animal
    """
    x, y = get_random_coordinates(grid=grid)
    
    while grid.entity_grid.get_position_value((x,y)):
        x, y = get_random_coordinates(grid=grid)
    
    return Animal(grid=grid, position=(x,y))
   
def get_random_coordinates(grid: Grid) -> Tuple[int,int]:
    """Get random coordinates of a point on a grid

    Args:
        grid (Grid): grid from which the coordinates will be chosen

    Returns:
        Tuple[int,int]: coordinates generated randomly
    """      
    return np.random.randint(0, grid.dimensions[0]), np.random.randint(0,grid.dimensions[1])
    
def init_trees(grid: Grid, count: int=0) -> None:
    """Initialize the population of trees

    Args:
        grid (Grid): grid on which the population will be initialized
        count (int, optional): number of trees to create. Defaults to 0.
    """    
    global tree_group
    tree_group = pg.sprite.Group()
    
    for _ in range(count):
        tree: Tree = create_new_tree(grid=grid)
        tree_group.add(tree)
    """ for i in range(0,5):
        tree_group.add(entities.Tree(grid=grid, position=(7,8+i)))
        tree_group.add(entities.Tree(grid=grid, position=(7+i,8)))
        tree_group.add(entities.Tree(grid=grid, position=(12,8+i)))
        tree_group.add(entities.Tree(grid=grid, position=(7+i,12))) """  
        
def create_new_tree(grid: Grid) -> Tree:
    """Create a new tree in a vacant cell

    Args:
        grid (Grid): grid on which the tree will be created

    Returns:
        Tree: the newly created tree
    """    
    x, y = get_random_coordinates(grid=grid)
    
    while grid.entity_grid.get_position_value((x,y)):
       x, y = get_random_coordinates(grid=grid)
    
    return Tree(grid=grid, position=(x,y))
    
def init_energies(grid: Grid) -> None:
    """Initialize the energies on the grid (only for tests)

    Args:
        grid (Grid): The grid on which the population will be initialized
    """
    global energy_group
    energy_group = grid.energy_group

    """ energy_group.add(BlueEnergy(grid=grid, position=(5,5)))
    energy_group.add(RedEnergy(grid=grid, position=(5,6))) """
           
def draw_world() -> None:
    """Draw the world, grid and entities"""
    draw_grid()
    draw_entities()
    draw_energies()
    
def draw_grid() -> None:
    """Draw the grid"""
    SCREEN.fill(WHITE)
    for x in range(0, WINDOW_WIDTH, BLOCK_SIZE):
        for y in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
            rect = pg.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pg.draw.rect(SCREEN, BLACK, rect, 1)

def update_world() -> None:
    """Update the world"""
    if tick_counter == 0:
        update_entities()

    #print(grid.grid.transpose())

def update_entities() -> None:
    """Update the entities"""
    animal_group.update()
        
def draw_entities() -> None:
    """Draw the entities"""
    animal_group.draw(SCREEN)
    tree_group.draw(SCREEN)

def draw_energies() -> None:
    """Draw the energies"""
    energy_group.draw(SCREEN)
  
if __name__ == "__main__":
    main()