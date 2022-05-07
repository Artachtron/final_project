from tkinter import RIGHT
import pygame as pg
from os.path import dirname, realpath, join
from pathlib import Path
from typing import Tuple
import enum
import random
import operator
import world


assets_path = join(Path(dirname(realpath(__file__))).parent.absolute(), "assets")

class Direction(enum.Enum):
    RIGHT = (1,0)
    LEFT = (-1,0)
    DOWN = (0,1)
    UP = (0,-1)
    
class Entity(pg.sprite.Sprite):
    def __init__(self,image_filename: str , grid: world.Grid, size: int=20, position: Tuple[int,int]=(int(world.GRID_WIDTH/2),int(world.GRID_HEIGHT/2))):
        super().__init__()
        self.size = size
        image = pg.image.load(join(assets_path,image_filename)).convert_alpha()
        self.image = pg.transform.scale(image, (size,size))
        self.position = position
        pos_x, pos_y = self.position
        self.rect = self.image.get_rect(center=(pos_x * world.BLOCK_SIZE + world.BLOCK_SIZE/2, pos_y * world.BLOCK_SIZE + world.BLOCK_SIZE/2))
        self.grid = grid
        self.grid.update_grid_cell(position=(self.position), value=1)
    

class Animal(Entity):
    def __init__(self, *args, **kwargs):
        super(Animal,self).__init__(image_filename='Animal.png',*args, **kwargs)
        
    """ def tmp_input(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            pass """
        
    def move(self, direction: Direction) -> None:
        """Move the animal in the given direction

        Args:
            direction (Direction): direction in which to move
        """
        next_move = tuple(map(operator.add, self.position, direction.value))
        if self._check_next_move(next_move=next_move):
            self.grid.update_grid_cell(position=(self.position), value=0)
            self.grid.update_grid_cell(position=next_move, value=1)
            self.position = next_move
                   
            self.rect.x = next_move[0]  * world.BLOCK_SIZE
            self.rect.y = next_move[1]  * world.BLOCK_SIZE
            
    def _check_next_move(self, next_move: Tuple[int,int]) -> bool:
        """Check if the next move is valid

        Args:
            next_move (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool: Validity of the next move
        """
        return self._is_cell_in_bounds(next_move=next_move) and self._is_vacant_cell(next_move=next_move)
     
    def _is_vacant_cell(self, next_move: Tuple[int,int])-> bool:
        """Check if a cell is vacant

        Args:
            next_move (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool: Vacancy of the cell
        """
        return not self.grid.get_position_status(position=next_move)
     
    def _is_cell_in_bounds(self, next_move: Tuple[int,int])-> bool:
        """Check if a cell is in the bounds of the grid

        Args:
            next_move (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool: Cell is inside the grid
        """
        next_x, next_y = next_move
        if next_x < 0 or next_x >= world.GRID_WIDTH or next_y < 0 or next_y >= world.GRID_HEIGHT:
            return False
        return True
        
    def update(self) -> None:
        """Update the Animal"""
        direction = random.choice(list(Direction))
        #print(direction)
        self.move(direction=direction)
        
class Tree(Entity):
    def __init__(self, *args, **kwargs):
        super(Tree, self).__init__(image_filename='Plant.png',*args, **kwargs)

       



        
 


