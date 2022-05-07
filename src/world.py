import pygame as pg
import sys
from entities import Animal, Tree
from energies import BlueEnergy, RedEnergy
#import src.entities, src.energies
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
    def __init__(self, height: int, width: int, block_size: int = BLOCK_SIZE):
        self._height = height
        self._width = width
        self.dimensions = (self._width, self._height)
        self._grid: np.array = np.zeros(self.dimensions, dtype=int)
        self.BLOCK_SIZE = block_size
    
    @property
    def grid(self) -> np.array:
        return self._grid
    
    @property
    def height(self) -> int:
        return self._height
    
    @property
    def width(self) -> int:
        return self._width
    
    def update_grid_cell_value(self, position: Tuple[int, int], value: int) -> None:
        """Update the value of a cell from the grid

        Args:
            position (Tuple[int, int]): The coordinates of the cell in the grid
            value (int): The new value to assign
        """
        try:
            self._grid[position] = value
        except IndexError:
            print("{position} is out of bounds")
        
    def get_position_value(self, position: Tuple[int, int]) -> int:
        """Get the value of a cell

        Args:
            position (Tuple[int, int]): The coordinates of the cell in the grid

        Returns:
            int: The value of the cell 0 for empty, 1 for full
        """
        try:
            return self._grid[position]
        except IndexError:
            print(f"{position} is out of bounds")
            return None
        
           

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
    grid: Grid = Grid(height=GRID_HEIGHT, width=GRID_WIDTH)
    
    init_population(grid=grid)
    init_energies(grid=grid)
 
def init_population(grid: Grid) -> None:
    """Populate the world with the initial population
    
    Args:
            grid (Grid): The grid on which the population will be initialized
    """
    global animal_group, tree_group
    
    animal_group = pg.sprite.Group()
    animal_group.add(Animal(grid=grid, position=(10,10)))
        
    tree_group = pg.sprite.Group()
    tree_group.add(Tree(grid=grid, position=(10,11)))
    """ for i in range(0,5):
        tree_group.add(entities.Tree(grid=grid, position=(7,8+i)))
        tree_group.add(entities.Tree(grid=grid, position=(7+i,8)))
        tree_group.add(entities.Tree(grid=grid, position=(12,8+i)))
        tree_group.add(entities.Tree(grid=grid, position=(7+i,12))) """
        
def init_energies(grid: Grid) -> None:
    """Initialize the energies on the grid (only for tests)

    Args:
        grid (Grid): The grid on which the population will be initialized
    """
    global energy_group
    energy_group = pg.sprite.Group()
    
    energy_group.add(BlueEnergy(grid=grid, position=(5,5)))
    energy_group.add(RedEnergy(grid=grid, position=(5,6)))
           
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