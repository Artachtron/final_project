import numpy as np
from typing import Tuple, Final, Any, Set , Dict
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
        
        self.dimensions: Tuple[int,int] = dimensions                # dimensions of the grid
        self.data_type = data_type                                  # type of data allowed on the grid
        self.initial_value = initial_value                          # value to fill the emtpy cells with
        self._array: np.array = np.full(self.dimensions,            # array containing the values
                                        fill_value=initial_value,
                                        dtype=data_type)
        
    @property
    def array(self) -> np.array:
        return self._array
    
    def _empty_cell(self, coordinates: Tuple[int, int]):
        """Private method:
            Emtpy the cell, putting it back to inital state

        Args:
            coordinates (Tuple[int, int]): coordinates of the cell to emtpy
        """        
        self._array[coordinates] = self.initial_value
            
    def _set_operation_valid(self, coordinates: Tuple[int, int], value: Any) -> bool:
        """Private method:
            Check if the set operation is valid, by applying 3 checks:
            - the coordinates are inside the bounds of the grid
            - the cell of given coordinates is free
            - the value is of valid type

        Args:
            coordinates (Tuple[int, int]):  coordinates to check for
            value (Any):                  value to check type of

        Returns:
            bool: True if all checks passed,
                  False if at least one check failed
        """        
        return (self.are_coordinates_in_bounds(coordinates=coordinates) and
                self.are_vacant_coordinates(coordinates=coordinates) and
                self._is_of_valid_type(value=value))
    
    def place_on_grid(self, value: Any) -> bool:
        """Place a given value on the grid, 
           based on its position

        Args:
            value (Any): value to place on the grid

        Returns:
            bool:   True if the value was placed on the grid
                    False if it couldn't place it
        """   
         
        coordinates: Tuple[int, int] = value.position() # position of the value
          
        return self._set_cell_value(coordinates=coordinates,
                                   value=value)
            
    def _is_of_valid_type(self, value: Any) -> bool:
        """Verify if the value's type is valid

        Args:
            value (Any): value of which to check type

        Returns:
            bool:   True if the value if of a valid type,
                    False if invalid type
        """        
        return Grid.is_subclass(value, self.data_type)
    
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
        
        if not (self.are_coordinates_in_bounds(coordinates=np.add(position,-radius)) and
                self.are_coordinates_in_bounds(coordinates=np.add(position, radius))):
            
            a = list(range(radius*2 + 1))  # List from (0, 2*radius)
            b = combinations(a*2, 2)       # ALl the combinations of coordinates
        
            subregion = self.get_sub_region(initial_pos=position,
                                            radius=radius) 
        
            # Optimised code to search if the cell at those coordinates contain an object
            # that is a subclass of the class given, if yes add it to the list of coordinates.
            # Avoid indexError when out of bounds
            positions = [tuple(np.add(position, coordinate)-1) for x, y in set(b) if
                        (subregion[coordinate:=tuple((x,y))]).__class__.__name__==
                                                            target_class.__name__]
        
        else:
        # Faster when no risk of indexError  
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
    
    def select_free_coordinates(self, position: Tuple[int, int],
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

    
    def update_cell(self, new_coordinate: Tuple[int, int], value: Any) -> bool:
        """Public method:
            Move an element from a cell to another,
            filling the new one and emptying the old one 

        Args:
            new_coordinate (Tuple[int, int]):   coordinates in which to move the element
            value (Any):                        value to move at different coordinates

        Returns:
            bool:   True if the element was moved successfully
                    False if it couldn't be move and nothing changed
        """        
        
        # try to insert the new value at the given coordinates        
        if success:= self._set_cell_value(coordinates=new_coordinate,
                                         value=value):

                            # Reset the old position
                            old_position = value.position()
                            self._empty_cell(coordinates=old_position)
                            
        return success
        
        
            
    def _set_cell_value(self, coordinates: Tuple[int, int], value: Any) -> bool:
        """Private method:
            Update the value of a cell from the grid

        Args:
            position (Tuple[int, int]): The coordinates of the cell in the grid
            value (int):                The new value to assign
            
        Returns:
            bool:   True if the value was successfully set
                    False if it couldn't be updated
        """
        if success:= self._set_operation_valid(coordinates=coordinates,
                                               value=value):
            try:
                self._array[coordinates] = value
            except IndexError:
                print("{coordinates} is out of bounds")
                
        return success
            
    def get_cell_value(self, coordinates: Tuple[int, int]) -> Any:
        """Public method:
            Get the value of a cell

        Args:
            position (Tuple[int, int]): The coordinates of the cell in the grid

        Returns:
            Any: value of the cell, None if empty
        """
        try:
            if coordinates[0] < 0 or coordinates[1] < 0:
                raise IndexError
            return self._array[tuple(coordinates)]
        except IndexError:
            print(f"{coordinates} is out of bounds")
            return False
        
    def get_sub_region(self, initial_pos: Tuple[int,int], radius:int=1) -> np.array:
        """Public method:
            Return an array around a given position of a defined size,
            even if the inital position is close from borders,
            pad with -1 values for cells out of boundaries

        Args:
            initial_pos (Tuple[int,int]):   position from which to search around
            radius (int, optional):         radius of search. Defaults to 1.

        Returns:
            np.array: padded subregion with dimensions depending only on radius
        """        
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
                 dimensions: Tuple[int,int]):
        
        self.__id = grid_id                                                     # unique identifier
        self.dimensions: Tuple[int,int] = dimensions                            # dimensions of the grid
        
        self._entity_grid: SubGrid = SubGrid(dimensions=self.dimensions,        # subgrid containing the entities
                                             data_type=Entity,
                                             initial_value=None)
        
        self._resource_grid: SubGrid = SubGrid(dimensions=self.dimensions,      # subgrid containing the resources
                                               data_type=Resource,
                                               initial_value=None)
        
        self._color_grid: SubGrid = SubGrid(dimensions=(*self.dimensions, 3),   # subgrid containing the color values
                                            data_type=np.uint8,
                                            initial_value=255)       
        
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
    
    @staticmethod
    def is_subclass(derived, base) -> bool:
        for cls in derived.__class__.__mro__[:-1]:
            if cls.__name__ == base.__name__:
                return True
        
        return False
    
    def place_on_resource(self, value:Any):
        self.resource_grid.place_on_grid(value=value)
        
    def place_on_entity(self, value:Any) :
        self.entity_grid.place_on_grid(value=value)
        
    def create_seed(self, coordinates: Tuple[int, int], genetic_data: Dict):
        seed = Seed(seed_id=genetic_data['tree_id'],
                    position=coordinates,
                    genetic_data=genetic_data)
        
        self.resource_grid._set_cell_value(coordinates=coordinates,
                                          value=seed)
         
        
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
          
        self.resource_grid._set_cell_value(coordinates=coordinates,
                                          value=energy)
                
    def remove_energy(self, energy: Energy) -> None:
        """Remove energy from the grid

        Args:
            energy (Energy): energy to remove
        """
        resource_grid = self.resource_grid
        position = energy._position()
        resource_grid._empty_cell(coordinates=position)
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
                entity = Animal(position=position,
                                size=size,
                                blue_energy=blue_energy,
                                red_energy=red_energy,
                                max_age=max_age,
                                adult_size=adult_size)
                
            case EntityType.Tree.value:
                production_type = production_type if production_type else np.random.choice(list(EnergyType))
                entity = Tree(production_type=production_type,
                              position=position,
                              size=size,
                              blue_energy=blue_energy,
                              red_energy=red_energy,
                              max_age=max_age)
                
            case EntityType.Seed.value:
                entity = Seed(position=position, blue_energy=blue_energy, red_energy=red_energy, max_age=max_age, production_type=production_type)
        
        self.entity_grid._set_cell_value(coordinates=entity.position(),
                                        value=entity)
        return entity
        
    def remove_entity(self, entity: Entity):
        """Remove entity from the grid

        Args:
            entity (Entity): entity to remove
        """
        entity_grid = self.entity_grid
        position = entity._position()
        entity_grid._empty_cell(coordinates=position)
        print(f"{entity} was deleted at {position}")
        
    def get_nearby_colors(self, radius: int = 1) -> np.array:
        position: Tuple[int, int] = self.position
        color_cells = []
                
        for x in range(-radius, radius + 1):
            for y in range(-radius, radius + 1):
                coordinate = tuple(np.add(position,(x, y)))
                color_cells.append(self.color_grid.get_cell_value(coordinate=coordinate))
                
        return np.array(color_cells)