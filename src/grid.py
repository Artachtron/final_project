import numpy as np
from typing import Tuple
from energies import BlueEnergy, RedEnergy, Energy, EnergyType
from entities import Entity, Animal, Tree
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
            
    def get_position_value(self, position: Tuple[int, int]) -> Entity|Energy:
        """Get the value of a cell

        Args:
            position (Tuple[int, int]): The coordinates of the cell in the grid

        Returns:
            int: The value of the cell 0 for empty, 1 for full
        """
        try:
            if position[0] < 0 or position[1] < 0:
                raise IndexError
            return self._subgrid[position]
        except IndexError:
            print(f"{position} is out of bounds")
            return False

        
class Grid:
    def __init__(self, height: int, width: int, block_size: int=20):
        self._height = height
        self._width = width
        self.dimensions = (self._width, self._height)
        
        self._entity_grid: SubGrid = SubGrid(dimensions=self.dimensions, dtype='entity')
        self._energy_grid: SubGrid = SubGrid(dimensions=self.dimensions, dtype='energy')
        self.BLOCK_SIZE = block_size
        
        self.energy_group = pg.sprite.Group()
        self.entity_group = pg.sprite.Group()
     
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
    
    def create_energy(self, energy_type: EnergyType, quantity: int, cell_coordinates: Tuple[int, int]):
        """Create energy on the grid

        Args:
            energy_type (EnergyType): type of energy to be created
            quantity (int): amount of energy to be created
            cell (Tuple[int, int]): cell of the grid on which the energy should be created
        """        
        print(f"{energy_type} was created at {cell_coordinates}")
        match energy_type.value:
            case EnergyType.BLUE.value:
                energy = BlueEnergy(grid=self, position=cell_coordinates, quantity=quantity)
            case EnergyType.RED.value:
                energy = RedEnergy(grid=self, position=cell_coordinates, quantity=quantity)
          
        self.energy_group.add(energy)

                
    def remove_energy(self, energy: Energy) -> None:
        """Remove energy from the grid

        Args:
            energy (Energy): energy to remove
        """
        energy_grid = self.energy_grid
        self.energy_group.remove(energy)
        position = energy.position
        energy_grid.update_grid_cell_value(position=position, value=None)
        print(f"{energy.type} was deleted at {position}")
    
    def create_entity(self, entity_type: str, position, size=1, blue_energy=5, red_energy=10) -> None:
        match entity_type:
            case "animal":
                entity = Animal(grid=self, position=position, size=size, blue_energy=blue_energy, red_energy=red_energy)
            case "tree":
                production_type = np.random.choice(list(EnergyType))
                entity = Tree(grid=self, production_type=production_type, position=position, size=size, blue_energy=blue_energy, red_energy=red_energy)
        
        self.entity_group.add(entity)
        return entity
        
    def remove_entity(self, entity):
        """Remove entity from the grid

        Args:
            entity (_type_): entity to remove
        """
        entity_grid = self.entity_grid
        self.entity_group.remove(entity)
        position = entity.position
        entity_grid.update_grid_cell_value(position=position, value=None)
        print(f"{entity} was deleted at {position}")