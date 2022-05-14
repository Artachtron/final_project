import numpy as np
from typing import Tuple
from energies import BlueEnergy, RedEnergy, Energy, EnergyType
from entities import Entity
import pygame as pg

class SubGrid:
    def __init__(self, dimensions: Tuple[int,int], dtype: str):
        self.dimensions = dimensions
        if dtype == 'entity' or dtype == 'entities':
            self._subgrid: np.array = np.full(self.dimensions, fill_value=None, dtype=Entity)
        elif dtype == 'energy' or dtype == 'energies':
            self._subgrid: np.array = np.full(self.dimensions, fill_value=None, dtype=Energy)
            
    @property
    def subgrid(self) -> np.array:
        return self._subgrid
    
    def update_grid_cell_value(self, position: Tuple[int, int], value: int) -> None:
        """Update the value of a cell from the grid

        Args:
            position (Tuple[int, int]): The coordinates of the cell in the grid
            value (int): The new value to assign
        """
        try:
            self._subgrid[position] = value
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
            return self._subgrid[position]
        except IndexError:
            print(f"{position} is out of bounds")
            return 0

        
class Grid:
    def __init__(self, height: int, width: int, block_size: int):
        self._height = height
        self._width = width
        self.dimensions = (self._width, self._height)
        
        self._entity_grid: SubGrid = SubGrid(dimensions=self.dimensions, dtype='entity')
        self._energy_grid: SubGrid = SubGrid(dimensions=self.dimensions, dtype='energy')
        self.BLOCK_SIZE = block_size
        
        self.energy_group = pg.sprite.Group()
        self.animal_group = pg.sprite.Group()
     
    @property
    def entity_grid(self) -> np.array:
        return self._entity_grid
   
    @property
    def energy_grid(self) -> np.array:
        return self._energy_grid
        
    @property
    def height(self) -> int:
        return self._height
    
    @property
    def width(self) -> int:
        return self._width
    
    def create_energy(self, energy_type: EnergyType, quantity: int, cell: Tuple[int, int]) -> None:
        """Create energy on the grid

        Args:
            energy_type (EnergyType): type of energy to be created
            quantity (int): amount of energy to be created
            cell (Tuple[int, int]): cell of the grid on which the energy should be created
        """        
        print(f"{energy_type} is created at {cell}")
        match energy_type.value:
            case "blue energy":
                self.energy_group.add(BlueEnergy(grid=self, position=cell, quantity=quantity))
            case "red energy":
                self.energy_group.add(RedEnergy(grid=self, position=cell, quantity=quantity))
            