import numpy as np
from typing import Tuple, Final
from energies import BlueEnergy, RedEnergy, Energy, EnergyType
from entities import Entity, Animal, Tree, Seed, EntityType
import pygame as pg

class SubGrid:
    def __init__(self, dimensions: Tuple[int,int], data_type: str, initial_value):
        self.dimensions: Tuple[int,int] = dimensions
        self._subgrid: np.array = np.full(self.dimensions, fill_value=initial_value, dtype=data_type)
     
    @property
    def subgrid(self) -> np.array:
        return self._subgrid
    
    def set_cell_value(self, cell_coordinates: Tuple[int, int], value: int) -> None:
        """Update the value of a cell from the grid

        Args:
            position (Tuple[int, int]): The coordinates of the cell in the grid
            value (int):                The new value to assign
        """
        try:
            self._subgrid[cell_coordinates] = value
        except IndexError:
            print("{cell_coordinates} is out of bounds")
            
    def get_cell_value(self, cell_coordinates: Tuple[int, int]) -> Entity|Energy:
        """Get the value of a cell

        Args:
            position (Tuple[int, int]): The coordinates of the cell in the grid

        Returns:
            int: The value of the cell 0 for empty, 1 for full
        """
        try:
            if cell_coordinates[0] < 0 or cell_coordinates[1] < 0:
                raise IndexError
            return self._subgrid[tuple(cell_coordinates)]
        except IndexError:
            print(f"{cell_coordinates} is out of bounds")
            return False
        
    def get_sub_region(self, initial_pos: Tuple[int,int], radius:int=1):
        x1, x2, y1, y2 = (initial_pos[0] - radius, initial_pos[0] + radius+1,
                          initial_pos[1] - radius, initial_pos[1] + radius+1)
        
        return self._subgrid[x1:x2, y1:y2]
        
class Grid:
    def __init__(self, height: int, width: int, block_size: int=20):
        self._height: int = height
        self._width: int = width
        self.dimensions: Tuple[int,int] = (self._width, self._height)
        
        self._entity_grid: SubGrid = SubGrid(dimensions=self.dimensions, data_type=Entity, initial_value=None)
        self._resource_grid: SubGrid = SubGrid(dimensions=self.dimensions, data_type=Energy, initial_value=None)
        self._color_grid: SubGrid = SubGrid(dimensions=(*self.dimensions, 3), data_type=np.uint8, initial_value=255)
        self.BLOCK_SIZE: Final[int] = block_size
        
        self.energy_group = pg.sprite.Group()
        self.entity_group = pg.sprite.Group()
     
    @property
    def entity_grid(self) -> np.array:
        return self._entity_grid
   
    @property
    def resource_grid(self) -> np.array:
        return self._resource_grid
    
    @property
    def color_grid(self) -> np.array:
        return self._color_grid
        
    @property
    def height(self) -> int:
        return self._height
    
    @property
    def width(self) -> int:
        return self._width
    
    def create_energy(self, energy_type: EnergyType, quantity: int, cell_coordinates: Tuple[int, int]):
        """Create energy on the grid

        Args:
            energy_type (EnergyType):   type of energy to be created
            quantity (int):             amount of energy to be created
            cell (Tuple[int, int]):     cell of the grid on which the energy should be created
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
        resource_grid = self.resource_grid
        self.energy_group.remove(energy)
        position = energy.position
        resource_grid.set_cell_value(cell_coordinates=position, value=None)
        print(f"{energy} was deleted at {position}")
    
    def create_entity(self, entity_type: str, position: Tuple[int, int], size: int=20,
                      blue_energy:int=Animal.INITIAL_BLUE_ENERGY, red_energy:int=Animal.INITIAL_RED_ENERGY,
                      max_age: int=0, production_type: EnergyType=None, adult_size: int=0) -> Tree|Animal|Seed:
        """Create an entity and add it to the grid

        Args:
            entity_type (str):                      type of entity to create (tree/animal)
            position (Tuple[int, int]):             position of the new entity on the grid
            size (int, optional): initial           size. Defaults to 1.
            blue_energy (int, optional):            amount of blue energy. Defaults to 5.
            red_energy (int, optional):             amout of red energy. Defaults to 10.
            production_type (EnergyType, optional): type of energy to be created by tree
            adult_size (int):                       size to reach before reaching adulthood. Defaults to 0
            
        Returns:
            Tree|Animal|Seed: entity newly created
        """        
              
        match entity_type:
            case EntityType.Animal.value:
                entity = Animal(grid=self, position=position, size=size, blue_energy=blue_energy, red_energy=red_energy, max_age=max_age, adult_size=adult_size)
            case EntityType.Tree.value:
                production_type = production_type if production_type else np.random.choice(list(EnergyType))
                entity = Tree(grid=self, production_type=production_type, position=position, size=size, blue_energy=blue_energy, red_energy=red_energy, max_age=max_age)
            case EntityType.Seed.value:
                entity = Seed(grid=self, position=position, blue_energy=blue_energy, red_energy=red_energy, max_age=max_age, production_type=production_type)
        
        self.entity_group.add(entity)
        return entity
        
    def remove_entity(self, entity: Entity):
        """Remove entity from the grid

        Args:
            entity (Entity): entity to remove
        """
        entity_grid = self.entity_grid
        self.entity_group.remove(entity)
        position = entity.position
        entity_grid.set_cell_value(cell_coordinates=position, value=None)
        print(f"{entity} was deleted at {position}")
        
    def get_nearby_colors(self, radius: int = 1) -> np.array:
        position: Tuple[int, int] = self.position
        color_cells = []
                
        for x in range(-radius, radius + 1):
            for y in range(-radius, radius + 1):
                coordinate = tuple(np.add(position,(x, y)))
                color_cells.append(self.color_grid.get_cell_value(coordinate=coordinate))
                
        return np.array(color_cells)