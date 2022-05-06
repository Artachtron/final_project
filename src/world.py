import pygame as pg
import sys
import entities
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

class Grid():
    def __init__(self):
        self._height: int = GRID_HEIGHT
        self._width: int = GRID_WIDTH
        self._grid: np.array = np.zeros((GRID_WIDTH, GRID_HEIGHT), dtype=int)
    
    @property
    def grid(self) -> np.array:
        return self._grid
    
    def update_grid_cell(self, position: Tuple[int, int], value: int) -> None:
        """Update the value of a cell from the grid

        Args:
            position (Tuple[int, int]): The coordinates of the cell in the grid
            value (int): The new value to assign
        """
        self._grid[position] = value
        
    def get_position_status(self, position: Tuple[int, int]) -> int:
        """Get the empty/full status of a cell

        Args:
            position (Tuple[int, int]): The coordinates of the cell in the grid

        Returns:
            int: The value of the cell 0 for empty, 1 for full
        """
        return self._grid[position]
           

def main():
    global tick_counter
    pg.init()
    init_world()
      
    tick_counter = 0

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
    global SCREEN, CLOCK
    SCREEN = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pg.time.Clock()
    grid: Grid = Grid()
    
    init_population(grid=grid)
 
def init_population(grid: Grid) -> None:
    """Populate the world with the initial population
    
    Args:
            grid (Grid): The grid on which the population will be initialized
    """
    
    global animal_group, tree_group
    
    animal_group = pg.sprite.Group()
    animal_group.add(entities.Animal(grid=grid))
        
    tree_group = pg.sprite.Group()
    tree_group.add(entities.Tree(grid=grid))
    """ for i in range(0,5):
        tree_group.add(entities.Tree(grid=grid, position=(7,8+i)))
        tree_group.add(entities.Tree(grid=grid, position=(7+i,8)))
        tree_group.add(entities.Tree(grid=grid, position=(12,8+i)))
        tree_group.add(entities.Tree(grid=grid, position=(7+i,12))) """
           
def draw_world() -> None:
    """Draw the world, grid and entities"""
    draw_grid()
    draw_entities()
    
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
  
if __name__ == "__main__":
    main()