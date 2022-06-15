import numpy as np
from typing import Tuple, Final, Any, Set 
from types import NoneType
from energies import BlueEnergy, RedEnergy, Energy, EnergyType, Resource
from entities import Entity, Animal, Tree, Seed, EntityType
import enum
from random import choice
from itertools import combinations

class SubGridType(enum.Enum):
    ENTITY = 0
    RESOURCE = 1
    COLOR = 2

class SubGrid:
    def __init__(self, dimensions: Tuple[int,int],
                 data_type: Any = Any,
                 initial_value: Any = None):
        
        self.dimensions: Tuple[int,int] = dimensions
        self._array: np.array = np.full(self.dimensions, fill_value=initial_value, dtype=data_type)
        self.data_type = data_type
        self.initial_value = initial_value
     
    @property
    def array(self) -> np.array:
        return self._array
    
    
    def are_available_coordinates(self, coordinates: Tuple[int, int]) -> bool:
        """Check if the coordinates correspond to valid cell,
           the cell has to be on the grid and be vacant

        Args:
            coordinates (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool:   True if the cell is on the grid and vacant,
                    False if the cell is not on the grid or occupied
        """
        return (self.are_coordinates_in_bounds(coordinates=coordinates) and
                self.are_vacant_coordinates(coordinates=coordinates))

    def are_vacant_coordinates(self, coordinates: Tuple[int, int]) -> bool:
        """Check if a cell is vacant

        Args:
            coordinates (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool:   True if the cell is vacant,
                    False if the cell is already occupied
        """
        return not self.get_cell_value(coordinates=coordinates)

    def are_coordinates_in_bounds(self, coordinates: Tuple[int, int]) -> bool:
        """Check if a cell is in the bounds of the grid

        Args:
            coordinates (Tuple[int,int]): Coordinates of the cell to check

        Returns:
            bool:   True if the coordinates are in the bounds of the grid,
                    False if the coordinates are out of the grid
        """
        x, y = coordinates
        
        return not (x < 0 or x >= self.dimensions[0] or
                    y < 0 or y >= self.dimensions[1])
 
    
    def _find_coordinates_with_class(self, target_class: Any, position: Tuple[int, int],
                                     radius: int = 1) -> Set[Tuple[int, int]]:
        """Private method:
            Find the list of cells at given radius distance from specified class

        Args:
            target_class (Any):         class to search for
            position (Tuple[int,int]):  starting position to look around
            radius (int, optional):     radius of search. Defaults to 1.

        Returns:
            Set[Tuple[int,int]]: set of found cells' coordinates
        """
        
        a = list(range(-radius, radius+1))  # List from (-radius, radius)
        b = combinations(a*2, 2)            # ALl the combinations of coordinates
    
        # Optimised code to search if the cell at those coordinates contain an object
        # that is a subclass of the class given, if yes add it to the list of coordinates
        positions = [coordinate for x, y in set(b) 
                     if (self.get_cell_value(
                         coordinate:=tuple(np.add(position,(x,y)))
                         ).__class__.__name__==
                          target_class.__name__)]

        return positions
    
    def find_free_coordinates(self, position: Tuple[int, int],
                              radius: int = 1) -> Set[Tuple[int, int]]:
        """Public method:
            Find a free cell in range

        Args:
            radius (int, optional):     radius of search. Defaults to 1.
            position (Tuple[int,int]):  starting position to look around

        Returns:
            Set[Tuple[int,int]]: set of free cells' coordinates
        """
        a = list(range(-radius, radius+1))  # List from (-radius, radius)
        b = combinations(a*2, 2)            # ALl the combinations of coordinates
        
        positions = [coordinate for x, y in set(b) 
                     if self.get_cell_value(coordinate:=tuple(np.add(position,(x,y)))) is None]
        
        return positions
    
    def select_free_coordinate(self, position: Tuple[int, int],
                               radius: int = 1) -> Tuple[int, int]:
        """Public method:
            Select randomly from the free cells available

        Args:
            radius (int, optional):     radius of search. Defaults to 1.
            position (Tuple[int,int]):  starting position to look around

        Returns:
            Tuple[int,int]: coordinates of the free cell
        """
        free_cells: Set[Tuple[int, int]] = self.find_free_coordinates(position=position,
                                                                      radius=radius)

        if free_cells:
            return choice(free_cells)
        
        return None

    
    def update_cell(self, new_coordinate: Tuple[int, int], value: Any) -> None:
                
        # Reset the old position
        old_position = value.position.vect
        self.set_cell_value(coordinates=old_position,
                            value=None)
        
        # Insert the new value at the given coordinates
        self.set_cell_value(coordinates=new_coordinate,
                            value=value)
            
    def set_cell_value(self, coordinates: Tuple[int, int], value: Any) -> None:
        """Update the value of a cell from the grid

        Args:
            position (Tuple[int, int]): The coordinates of the cell in the grid
            value (int):                The new value to assign
        """
        try:
            self._array[coordinates] = value
        except IndexError:
            print("{coordinates} is out of bounds")
            
    def get_cell_value(self, coordinates: Tuple[int, int]) -> Any:
        """Get the value of a cell

        Args:
            position (Tuple[int, int]): The coordinates of the cell in the grid

        Returns:
            Any: The value of the cell, None is empty
        """
        try:
            if coordinates[0] < 0 or coordinates[1] < 0:
                raise IndexError
            return self._array[tuple(coordinates)]
        except IndexError:
            print(f"{coordinates} is out of bounds")
            return False
        
    def get_sub_region(self, initial_pos: Tuple[int,int], radius:int=1) -> np.array:
        x1, x2, y1, y2 = (initial_pos[0] - radius, initial_pos[0] + radius+1,
                          initial_pos[1] - radius, initial_pos[1] + radius+1)
        
        ndim = self._array.ndim
        if ndim == 3:
            width, height, depth = self.dimensions
            padded_subregion = np.full(fill_value=-255, shape=(x2-x1, y2-y1, depth))
        elif ndim == 2:
            width, height = self.dimensions
            padded_subregion = np.full(fill_value=None, shape=(x2-x1, y2-y1))
            
        left_pad = right_pad = up_pad = down_pad = 0
        
        if x1 < 0:
            left_pad = -x1
            x1=0
        if x2 > width:
            right_pad = x2 - width
            x2 = width
        if y1 < 0:
            up_pad = -y1
            y1 = 0
        if y2 > height:
            down_pad = y2 - height
            y2 = height
    
        subregion = self._array[x1:x2, y1:y2]
        
        x_shape, y_shape = subregion.shape[:2]
        
        for x in range(x_shape):
            for y in range(y_shape):
                padded_subregion[x+left_pad, y+up_pad] = subregion[x-right_pad,y-down_pad]
                
        return padded_subregion
            
class Grid:
    def __init__(self,
                 grid_id: int,
                 dimensions: Tuple[int,int],
                 block_size: int=20):
        
        self.__id = grid_id
        self.dimensions: Tuple[int,int] = dimensions
        
        self._entity_grid: SubGrid = SubGrid(dimensions=self.dimensions,
                                             data_type=Entity,
                                             initial_value=None)
        
        self._resource_grid: SubGrid = SubGrid(dimensions=self.dimensions,
                                               data_type=Resource,
                                               initial_value=None)
        
        self._color_grid: SubGrid = SubGrid(dimensions=(*self.dimensions, 3),
                                            data_type=np.uint8,
                                            initial_value=255)
        
        self.BLOCK_SIZE: Final[int] = block_size
        
        """ self.energy_group = pg.sprite.Group()
        self.entity_group = pg.sprite.Group() """
    
    @property
    def id(self):
        return self.__id
     
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
    def width(self) -> int:
        return self.dimensions[0]
    
    @property
    def height(self) -> int:
        return self.dimensions[1]
        
    def create_energy(self, energy_type: EnergyType, quantity: int, coordinates: Tuple[int, int]):
        """Create energy on the grid

        Args:
            energy_type (EnergyType):   type of energy to be created
            quantity (int):             amount of energy to be created
            cell (Tuple[int, int]):     cell of the grid on which the energy should be created
        """        
        print(f"{energy_type} was created at {coordinates}")
        match energy_type.value:
            case EnergyType.BLUE.value:
                energy = BlueEnergy(energy_id=0,
                                    position=coordinates,
                                    quantity=quantity)
                
            case EnergyType.RED.value:
                energy = RedEnergy(energy_id=0,
                                   position=coordinates,
                                   quantity=quantity)
          
        self.resource_grid.set_cell_value(coordinates=coordinates,
                                          value=energy)
                
    def remove_energy(self, energy: Energy) -> None:
        """Remove energy from the grid

        Args:
            energy (Energy): energy to remove
        """
        resource_grid = self.resource_grid
        self.energy_group.remove(energy)
        position = energy._position
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
                entity = Animal(position=position, size=size, blue_energy=blue_energy, red_energy=red_energy, max_age=max_age, adult_size=adult_size)
            case EntityType.Tree.value:
                production_type = production_type if production_type else np.random.choice(list(EnergyType))
                entity = Tree(production_type=production_type, position=position, size=size, blue_energy=blue_energy, red_energy=red_energy, max_age=max_age)
            case EntityType.Seed.value:
                entity = Seed(position=position, blue_energy=blue_energy, red_energy=red_energy, max_age=max_age, production_type=production_type)
        
        self.entity_grid.set_cell_value(coordinates=entity.position(),
                                        value=entity)
        return entity
        
    def remove_entity(self, entity: Entity):
        """Remove entity from the grid

        Args:
            entity (Entity): entity to remove
        """
        entity_grid = self.entity_grid
        self.entity_group.remove(entity)
        position = entity._position
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