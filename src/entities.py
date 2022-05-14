import pygame as pg
from os.path import dirname, realpath, join
from pathlib import Path
from typing import Tuple
import enum
import random
from energies import EnergyType, Energy
import numpy as np


assets_path = join(Path(dirname(realpath(__file__))).parent.absolute(), "assets/models/entities")

class Direction(enum.Enum):
    RIGHT = (1,0)
    LEFT = (-1,0)
    DOWN = (0,1)
    UP = (0,-1)
    
class Entity(pg.sprite.Sprite):
    def __init__(self,
                 image_filename: str,
                 grid,
                 position: Tuple[int,int],
                 size: int=20,
                 blue_energy: int=10,
                 red_energy: int=10,
                 ):
        super().__init__()
        self.size = size
        self.position = position
        
        image = pg.image.load(join(assets_path, image_filename)).convert_alpha()
        self.image = pg.transform.scale(image, (size,size))
        pos_x, pos_y = self.position
        self.rect = self.image.get_rect(center=(pos_x * grid.BLOCK_SIZE + grid.BLOCK_SIZE/2, pos_y * grid.BLOCK_SIZE + grid.BLOCK_SIZE/2))
        
        self.grid = grid
        self.entity_grid = grid.entity_grid
        self.entity_grid.update_grid_cell_value(position=(self.position), value=self)
        
        self._energies_stock = {"blue energy": blue_energy, "red energy": red_energy}
        
    @property
    def energies_stock(self):
        return self._energies_stock

    def get_blue_energy(self):
        return self._energies_stock["blue energy"]
    
    def get_red_energy(self):
        return self._energies_stock["red energy"]
    
    def drop_energy(self, energy_type: EnergyType, quantity: int, cell_coordinates: Tuple[int,int]) -> None:
        """Drop some energy on a cell

        Args:
            energy_type (EnergyType): the type of energy (blue/red) to drop
            quantity (int): the amount of energy to drop
            cell_coordinates (Tuple[int,int]): the coordinates of the cell on which to drop energy
        """        
        if self._check_coordinates(coordinates=cell_coordinates, subgrid=self.grid.energy_grid):
            self.loose_energy(energy_type=energy_type, quantity=quantity)   
                
            self.grid.create_energy(energy_type=energy_type, quantity=quantity, cell=cell_coordinates)
            
    def pick_up_energy(self, cell_coordinates: Tuple[int, int]) -> None:
        """Pick energy up from a cell

        Args:
            cell_coordinates (Tuple[int, int]): coordinates of the cell from which to pick up energy
        """
        energy_grid = self.grid.energy_grid
        energy: Energy = energy_grid.get_position_value(position=cell_coordinates)
        if energy:
            self.energies_stock[energy.type.value] += energy.quantity
            energy_grid.update_grid_cell_value(position=cell_coordinates, value=None)
            
    def loose_energy(self, energy_type: EnergyType, quantity: int) -> None:
        """Loose energy from energies stock

        Args:
            energy_type (EnergyType): the type of energy to loose
            quantity (int): amount of energy to loose
        """
        energy_amount = self._energies_stock[energy_type.value]
        if energy_amount - quantity > 0:
            self._energies_stock[energy_type.value] -= quantity
        else:
            quantity = energy_amount
            self._energies_stock[energy_type.value] = 0 
        
        

class Animal(Entity):
    def __init__(self, *args, **kwargs):
        super(Animal, self).__init__(image_filename='Animal.png',*args, **kwargs)
        
    """ def tmp_input(self):
        keys = pg.key.get_pressed()
        if keys[pg.K_UP]:
            pass """
        
    def move(self, direction: Direction) -> None:
        """Move the animal in the given direction

        Args:
            direction (Direction): direction in which to move
        """
        next_move = tuple(np.add(self.position, direction.value))
        if self._check_coordinates(coordinates=next_move, subgrid=self.grid.entity_grid):
            self.entity_grid.update_grid_cell_value(position=(self.position), value=None)
            self.entity_grid.update_grid_cell_value(position=next_move, value=self)
            self.position = next_move
                   
            self.rect.x = next_move[0]  * self.grid.BLOCK_SIZE
            self.rect.y = next_move[1]  * self.grid.BLOCK_SIZE
            
    def _check_coordinates(self, coordinates: Tuple[int,int], subgrid) -> bool:
        """Check if the next move is valid

        Args:
            next_move (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool: Validity of the next move
        """
        return self._is_cell_in_bounds(next_move=coordinates, subgrid=subgrid) and self._is_vacant_cell(next_move=coordinates, subgrid=subgrid)
     
    def _is_vacant_cell(self, subgrid, next_move: Tuple[int,int])-> bool:
        """Check if a cell is vacant

        Args:
            next_move (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool: Vacancy of the cell
        """
        return not subgrid.get_position_value(position=next_move)
     
    def _is_cell_in_bounds(self, subgrid, next_move: Tuple[int,int])-> bool:
        """Check if a cell is in the bounds of the grid

        Args:
            next_move (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool: Cell is inside the grid
        """
        next_x, next_y = next_move
        if next_x < 0 or next_x >= subgrid.dimensions[0] or next_y < 0 or next_y >= subgrid.dimensions[1]:
            return False
        return True
        
    def update(self) -> None:
        """Update the Animal"""
        self.test_update()
        
    def test_update(self) -> None:
        """Test behaviour by doing random actions"""
        direction = random.choice(list(Direction))
        #print(direction)
        if np.random.uniform() < 0.01:
            x, y = np.random.randint(-2,2), np.random.randint(-2,2)
            coordinates = tuple(np.add(self.position, (x,y)))
            if self._check_coordinates(coordinates=coordinates, subgrid=self.grid.energy_grid):
                self.drop_energy(energy_type=np.random.choice(EnergyType), cell_coordinates=coordinates, quantity=1)
        self.move(direction=direction)
        
class Tree(Entity):
    def __init__(self, *args, **kwargs):
        super(Tree, self).__init__(image_filename='Plant.png',*args, **kwargs)

       



        
 


