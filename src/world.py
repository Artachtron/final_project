import pygame as pg
import sys
import entities
import numpy as np
from typing import Tuple

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

GRID_HEIGHT = 20
GRID_WIDTH = 20
BLOCK_SIZE = 20

SIM_SPEED = 20

WINDOW_HEIGHT = BLOCK_SIZE * GRID_HEIGHT
WINDOW_WIDTH = BLOCK_SIZE * GRID_WIDTH

class Grid():
    def __init__(self):
        self._height = GRID_HEIGHT
        self._width = GRID_WIDTH
        self._grid = np.zeros((GRID_WIDTH, GRID_HEIGHT), dtype=int)
    
    @property
    def grid(self) -> np.array:
        return self._grid
    
    def update_grid(self, position: Tuple[int, int], value: int) -> None:
        self._grid[position] = value
        
    def get_position_status(self, position):
        return self._grid[position]
           

def main():
    global SCREEN, CLOCK, counter, animal_group, tree_group
    
    pg.init()
    SCREEN = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pg.time.Clock()
    SCREEN.fill(WHITE)
    grid = Grid()
     
    animal_group = pg.sprite.Group()

    animal_group.add(entities.Animal(grid=grid))
    #animal_group.add(entities.Animal(grid=grid))
        
    tree_group = pg.sprite.Group()
    tree_group.add(entities.Tree(grid=grid))
    tree_group.add(entities.Tree(grid=grid, position=(10,11)))
  
    counter = 0

    while True:
        draw_world()
        update_world(grid=grid)
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

        pg.display.update()
        CLOCK.tick(60)
        counter += 1
        if counter == SIM_SPEED:
            counter = 0
            
def draw_world() -> None:
    draw_grid()
    draw_entities()
    
def draw_grid() -> None:
    SCREEN.fill(WHITE)
    for x in range(0, WINDOW_WIDTH, BLOCK_SIZE):
        for y in range(0, WINDOW_HEIGHT, BLOCK_SIZE):
            rect = pg.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pg.draw.rect(SCREEN, BLACK, rect, 1)

def update_world(grid: Grid) -> None:
    if counter == 0:
        update_entities()
        update_grid(grid=grid)
    
def update_grid(grid: Grid) -> None:
    for animal in animal_group:
        grid.update_grid(position=(animal.position), value=1)
    for tree in tree_group:
        grid.update_grid(position=(tree.position), value=1)

    #print(grid.grid.transpose())

def update_entities() -> None:
    animal_group.update()
        
def draw_entities() -> None:
    animal_group.draw(SCREEN)
    tree_group.draw(SCREEN)
  
if __name__ == "__main__":
    main()